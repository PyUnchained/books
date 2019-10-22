from django.db import models

class SystemAccount(models.Model):
	name = models.CharField(max_length = 200)
	password = models.CharField(max_length = 300)
	email = models.EmailField()
	settings = models.OneToOneField('AccountSettings', models.CASCADE)
	created = models.DateTimeField(auto_now_add = True)

class AccountSettings(models.Model):
	financial_year_start = models.DateField()