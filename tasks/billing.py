import datetime
from dateutil import relativedelta

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
def update_billing_status(user_pk, current_date = None):
    """ Updates the current billing status of an account
    
    Parameters
    ----------

    billing_account_pk: Str, required
    current_date: Str, optional
        - Any format in settings.DATE_INPUT_FORMATS
        - Sets the current date to use. Defaults to today

    Returns
    -------
    A Boolean representing whether or not the billing status needed updating

    Raises
    ------

    ValueError - Raised when the current date's format does not match any in 
        settings.DATE_INPUT_FORMATS
    """
    
    if not current_date:
        current_date = timezone.now().date()
    else:
        for date_format in settings.DATE_INPUT_FORMATS:
            try:
                current_date = datetime.datetime.strptime(current_date, date_format).date()
                break
            except:
                pass

        # Raise error if not converted to a date object
        if isinstance(current_date, str) :
            raise ValueError(f'Failed to convert current_date string {current_date} '
                'to date object. Is the given format defined in settings.DATE_INPUT_FORMATS?')

    # Iterate through all the user's active accounts
    user = User.objects.get(pk = user_pk)
    invoice_entries = []
    double_entries = []
    central_account = get_internal_system_account()
    earliest_due_date = timezone.now().date() + relativedelta.relativedelta(years = 2)
    active_billing_accounts = BillingAccount.objects.filter(
        user = user, active = True)

    user_accounts_payable = central_account.get_account(code = f'2000 - {user.username}')
    sales_account = central_account.get_account(code = '4000')

    for billing_account in active_billing_accounts:

        # Determine if the account needs to be billed again
        billing_required = False

        if current_date >= billing_account.next_billed:
            billing_required = True

        # If this account doesn't need an update, end here
        if not billing_required:
            continue



        # Determine how much to charge for the elapsed time
        months_to_bill = relativedelta.relativedelta(current_date,
            billing_account.last_billed).months
        total = billing_account.billing_tier.unit_price*months_to_bill

        # Determine due date
        due = current_date + datetime.timedelta(
            days = billing_account.billing_method.days_till_due)
        if due < earliest_due_date:
            earliest_due_date = due

        # Create the entry as it will appear on the invoice
        entry_details = {'description':f"{billing_account.product_description}",
            'quantity':months_to_bill, 'total': float(total),
            'unit_price':float(billing_account.billing_tier.unit_price),
            'billing_account':billing_account.pk}
        invoice_entries.append(entry_details)

        # Create double entry for accounting system
        debit_entry = {'account':user_accounts_payable, 'value':total,
            'details':f"{billing_account.product_description} (SystemBilling)"}
        credit_entry = {'account':sales_account, 'value':total,
            'details':f"{billing_account.user.username} "
                f"{billing_account.product_description} (SystemBilling)"}
        double_entry_dict = {'debits':[debit_entry], 'credits': [credit_entry],
            'details': f"Billing for {billing_account.product_description}",
            'date':current_date, 'system_account':central_account}
        double_entries.append(double_entry_dict)

    # Happens when there is nothing to invoice in this run
    if not invoice_entries:
        return False

    with transaction.atomic():

        # Generate an invoice
        invoice = Invoice.objects.create(
            due = earliest_due_date, date = current_date,
            entries = invoice_entries)
        for acc in active_billing_accounts:
            invoice.billing_accounts.add(acc)

        # Record the invoicing of the client in the accounts
        for de_dict in double_entries:
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