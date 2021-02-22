from django.db import models
from django.conf import settings

class BillingAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    billing_method = models.ForeignKey('books.BillingMethod', models.SET_NULL, null = True)
    charge = models.DecimalField(max_digits = 20, decimal_places = 2)
    created = models.DateTimeField(auto_now_add = True)
    up_to_date = models.BooleanField(default = True)
    active = models.BooleanField(default = True)

class BillingMethod(models.Model):
    description = models.CharField(max_length = 100)
    time = models.TimeField()
    day_of_month = models.IntegerField(default = 1)
    billing_period = models.IntegerField(default = 1)
    grace_period = models.IntegerField(default = 14)

    def __str__(self):
        return self.description

class Invoice(models.Model):
    billing_account = models.ForeignKey('books.BillingAccount',
        models.CASCADE)
    due = models.DateTimeField()
    value = models.DecimalField(max_digits = 20, decimal_places = 2)
    paid = models.BooleanField()
    file = models.FileField(upload_to = 'books/generated/invoices')
    created = models.DateTimeField(auto_now_add = True)

class Receipt(models.Model):
    invoice = models.ForeignKey('books.Invoice', models.CASCADE)
    file = models.FileField(upload_to = 'books/generated/receipts')
    created = models.DateTimeField(auto_now_add = True)