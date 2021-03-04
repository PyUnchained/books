import datetime
import math
from dateutil import relativedelta
from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

from celery import shared_task

from books.models import BillingAccount, Invoice, DoubleEntry
from books.virtual.pdf import InvoiceBuilder
from books.utils.celery_task import TestAwareTask
from books.utils import get_internal_system_account

User = get_user_model()

@shared_task
def update_billing_status(current_date = None, account_pks = []):
    """ Updates the current billing status of an account
    
    Parameters
    ----------

    account_pks: List, optional
    current_date: Str, Date or Datetime, optional
        - Any format in settings.DATE_INPUT_FORMATS
        - Sets the current date to use. Defaults to today

    Returns
    -------
    A Boolean representing whether or not any billing accounts were updated

    Raises
    ------

    ValueError - Raised when the current date's format does not match any in 
        settings.DATE_INPUT_FORMATS
    """
    all_billing_data = {}
    updates_required = False # Whether or not any account was updated
    
    if not current_date:
        current_date = timezone.now().date()
    else:
        # Raise error if not converted to a date object
        if isinstance(current_date, str):
            for date_format in settings.DATE_INPUT_FORMATS:
                try:
                    current_date = datetime.datetime.strptime(current_date, date_format).date()
                    break
                except:
                    pass

            if isinstance(current_date, str):
                raise ValueError(f'Failed to convert current_date string {current_date} '
                    'to date object. Is the given format defined in settings.DATE_INPUT_FORMATS?')
        else:
            if isinstance(current_date, datetime.datetime): # Make sure it's a date, not datetime
                current_date = current_date.date()
            
    central_account = get_internal_system_account()
    sales_account = central_account.get_account(code = '4000')

    if account_pks:
        account_qs = {'pk__in':account_pks}
    else:
        account_qs = {}
    target_billing_accounts = BillingAccount.objects.filter(**account_qs)

    def get_user_billing_info(user):
        """ Retrieves the accounts receivable account and as well as its current balance. """

        if user not in all_billing_data:
            account = central_account.get_account(code = f'1200 - {user.username}')
            balance = account.balance(as_at = current_date)
            all_billing_data[user] = {'account' : (account, balance),
                'invoice_entries' : [], 'double_entries' : [],
                'due' : None, 'updated_billing_accounts' : []}
        return all_billing_data[user]

    for billing_account in target_billing_accounts:

        # Determine if the account needs to be billed again or the grace period has
        # expired
        user_billing_data = get_user_billing_info(billing_account.user)
        user_accounts_receivable, user_current_balance = user_billing_data['account']
        billing_required = False
        grace_period_expired = False

        if current_date >= billing_account.next_billed:
            billing_required = True

        if current_date > billing_account.last_billed + relativedelta.relativedelta(
            days = billing_account.billing_method.grace_period):
            grace_period_expired = True

        # Accounts with a remaining balance should remain active. Only those
        # that are in areas and have exceeded the grace period are deactivated
        if user_current_balance <= Decimal("0.00"):
            billing_account.active = True
        elif grace_period_expired:
            billing_account.active = False

        if not billing_required:
            billing_account.save() # Active state might have changed
            continue
        
        # Work out details for the invoice to be generated over this billing period
        periods_to_bill = relativedelta.relativedelta(current_date,
            billing_account.last_billed).months/billing_account.billing_method.billing_period
        periods_to_bill = Decimal(str(math.floor(periods_to_bill)))
        total = billing_account.billing_tier.unit_price*periods_to_bill
        print (periods_to_bill)

        # Select the earliest due date if more than one billing account included in invoice
        due = current_date + datetime.timedelta(
            days = billing_account.billing_method.days_till_due)
        if not user_billing_data['due']:
            user_billing_data['due'] = due
        elif due < user_billing_data['due']:
            user_billing_data['due'] = due


        # Create the entry as it will appear on the invoice. Convert Decimals
        # to JSON serializable floats or ints
        entry_details = {'description':f"{billing_account.product_description}",
            'quantity':int(periods_to_bill), 'total': float(total),
            'unit_price':float(billing_account.billing_tier.unit_price),
            'billing_account':billing_account.pk}
        user_billing_data['invoice_entries'].append(entry_details)

        # Create double entry for accounting system
        debit_entry = {'account':user_accounts_receivable, 'value':float(total),
            'details':f"{billing_account.product_description} (SystemBilling)"}
        credit_entry = {'account':sales_account, 'value':float(total),
            'details':f"{billing_account.user.username} "
                f"{billing_account.product_description} (SystemBilling)"}
        double_entry_dict = {'debits':[debit_entry], 'credits': [credit_entry],
            'details': f"Billing for {billing_account.product_description}",
            'date':current_date, 'system_account':central_account}
        user_billing_data['double_entries'].append(double_entry_dict)

        # Determine the next time the account will have to billed
        billing_account.next_billed = current_date + relativedelta.relativedelta(
            months = billing_account.billing_method.billing_period)
        billing_account.last_billed = current_date
        user_billing_data['updated_billing_accounts'].append(billing_account)
        updates_required = True

    if not updates_required:
        return False

    for user, user_billing_data in all_billing_data.items():
        with transaction.atomic():
            # Generate an invoice
            invoice = Invoice.objects.create(
                due = user_billing_data['due'], date = current_date,
                entries = user_billing_data['invoice_entries'])
            for acc in user_billing_data['updated_billing_accounts']:
                acc.save()
                invoice.billing_accounts.add(acc)

            # Record the invoicing of the client in the accounts
            for de_dict in user_billing_data['double_entries']:
                DoubleEntry.record(**de_dict)

    return True


@shared_task(base = TestAwareTask)
def generate_invoice_pdf(invoice_entries = [], due = None, date = None, invoice_pk = None):
    """ Create PDF version of the invoice and associate it with an Invoice instance """

    # Calculate invoice number
    invoice = Invoice.objects.get(pk = invoice_pk)
    invoice_num = invoice.pk

    
    file_name = f'invoice_{invoice_num}.pdf'
    builder = InvoiceBuilder()

    content_file = builder.build([], file_name = file_name,
        invoice_num = invoice_num, invoice_entries = invoice_entries,
        due = due, date = date)

    invoice.file.save(file_name, content_file)