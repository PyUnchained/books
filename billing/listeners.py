import json
from dateutil import relativedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from books.models.billing import BillingAccount, Invoice
from books.tasks.billing import generate_invoice_pdf
from books.utils import get_internal_system_account

@receiver(pre_save, sender = BillingAccount)
def next_billing_date_on_init(sender, instance, raw, *args, **kwargs):
    """ Sets the next billing date for the account when it is first being created. """

    if raw:
        return

    is_new = instance.pk == None
    if is_new:
        if not instance.last_billed:
            instance.last_billed = instance.start_date - relativedelta.relativedelta(
                days = 1)
        instance.next_billed = instance.start_date

@receiver(post_save, sender = BillingAccount)
def check_accounts_receivable_exists(sender, instance, raw, *args, **kwargs):
    """ Verifies that an Accounts Payable account has been created for this user. """

    if raw:
        return

    central_account = get_internal_system_account()
    accounts_receivable = central_account.get_account(code = '1200')
    central_account.create_subaccount(accounts_receivable,
        name = f'Accounts Receivable - ({instance.user})',
        code_suffix = instance.user.username )


@receiver(post_save, sender = Invoice)
def update_invoice_file(sender, instance, raw, *args, **kwargs):

    if raw:
        return

    if not instance.file:
        generate_invoice_pdf.delay(invoice_entries = instance.entries,
            due  = instance.due, date = instance.date, invoice_pk = instance.pk)
