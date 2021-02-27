import datetime
from dateutil import relativedelta

from django.utils import timezone
from django.conf import settings
from django.db import transaction

from celery import shared_task

from books.models.billing import BillingAccount, Invoice
from books.virtual.pdf import InvoiceBuilder

@shared_task
def update_billing_status(billing_account_pk, current_date = None):
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

    # Determine if the account needs to be billed again
    billing_account = BillingAccount.objects.get(pk = billing_account_pk)
    billing_required = False

    if current_date >= billing_account.next_billed:
        billing_required = True

    # If this account doesn't need an update, end here
    if not billing_required:
        return False

    # Create the invoice
    with transaction.atomic():

        # Determine how much to charge for the elapsed time
        months_to_bill = relativedelta.relativedelta(current_date,
            billing_account.last_billed).months
        total = billing_account.billing_tier.unit_price*months_to_bill

        due_date = billing_account.next_billed + datetime.timedelta(
            days = billing_account.billing_method.days_till_due)

        invoice_entries = [{'description':f"{billing_account.product_description}",
            'quantity':months_to_bill, 'total': float(total),
            'unit_price':float(billing_account.billing_tier.unit_price)}]

        invoice = Invoice.objects.create(billing_account = billing_account,
            due = due_date, date = billing_account.next_billed,
            entries = invoice_entries)

    return True

@shared_task
def generate_invoice_pdf(invoice_pk):
    invoice = Invoice.objects.get(pk = invoice_pk)
    builder = InvoiceBuilder()
    builder.build([], file_name = 'invoice.pdf', invoice = invoice)