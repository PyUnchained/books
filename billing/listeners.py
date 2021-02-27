import json
from dateutil import relativedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from books.models.billing import BillingAccount, Invoice
from books.tasks.billing import generate_invoice_pdf
from books.utils.runtime import is_test

@receiver(pre_save, sender = BillingAccount)
def next_billing_date_on_init(sender, instance, raw, *args, **kwargs):
    """ Sets the next billing date for the account when it is first being created. """

    if raw:
        return

    is_new = instance.pk == None
    if is_new:

        if instance.last_billed:
            last_billed_date = instance.last_billed
        else:
            last_billed_date = instance.start_date

        next_billed = last_billed_date + relativedelta.relativedelta(
            months=instance.billing_method.billing_period)
        instance.next_billed = next_billed

@receiver(post_save, sender = Invoice)
def update_invoice_file(sender, instance, raw, *args, **kwargs):

    if raw:
        return
    generate_invoice_pdf(instance.pk)
    generate_invoice_pdf.delay(instance.pk)

