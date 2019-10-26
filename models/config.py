from django.db import models

class AccountSettings(models.Model):
    financial_year_start = models.DateField()