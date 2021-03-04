from dateutil import relativedelta

from django.utils import timezone
from django.db import models
from django.conf import settings

def today():
    return timezone.now().date()

class BillingAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    product_description = models.CharField(max_length = 100,
        help_text = "What the user will be billed for (appears in description of invoice)")
    billing_method = models.ForeignKey('books.BillingMethod', models.SET_NULL, null = True)
    billing_tier = models.ForeignKey('books.BillingTier', models.SET_NULL, null = True)
    created = models.DateTimeField(auto_now_add = True)
    start_date = models.DateField(default = today)
    up_to_date = models.BooleanField(default = True)
    last_billed = models.DateField(blank = True, null = True)
    next_billed = models.DateField(blank = True, null = True)
    active = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.user.username} - {self.product_description}"

    @property
    def due(self):
        try:
            due = self.next_billed + relativedelta.relativedelta(
                    days = self.billing_method.grace_period)
        except:
            due = None
        return due

class BillingMethod(models.Model):
    description = models.CharField(max_length = 100)
    billing_period = models.IntegerField(default = 1)
    days_till_due = models.IntegerField(default = 30)
    grace_period = models.IntegerField(default = 14)

    def __str__(self):
        return self.description

class BillingTier(models.Model):
    description = models.CharField(max_length = 100)
    unit_price = models.DecimalField(max_digits = 20, decimal_places = 2)

class Invoice(models.Model):
    billing_accounts = models.ManyToManyField('books.BillingAccount', blank = True)
    due = models.DateField()
    date = models.DateField()
    entries = models.JSONField(help_text = "A list of dictionaries with the following keys: "
        "description, quantity, unit_price, total, billing_account")
    paid = models.BooleanField(default = False)
    file = models.FileField(upload_to = 'books/generated/invoices', blank = True, null = True)
    created = models.DateTimeField(auto_now_add = True)

class Receipt(models.Model):
    invoice = models.ForeignKey('books.Invoice', models.CASCADE)
    file = models.FileField(upload_to = 'books/generated/receipts')
    created = models.DateTimeField(auto_now_add = True)

