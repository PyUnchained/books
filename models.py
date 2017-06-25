import uuid
from decimal import Decimal
from django.db import models

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS

# Create your models here.
class OpexaBooksSystem(models.Model):
	system_code = models.CharField(primary_key = True, default=uuid.uuid4,
		max_length = 2000)

class AccountType(models.Model):
	name = models.CharField(max_length = 100, primary_key = True)
	description = models.CharField(max_length = 300, blank = True, null = True)

	def __str__(self):
		return self.name

class Account(models.Model):
	code = models.CharField(max_length = 100,
		primary_key = True)
	name = models.CharField(max_length = 120)
	account_type = models.ForeignKey('AccountType', null = True)

	def __str__(self):
		return self.name

	@property
	def balance(self):
		debit_entries = JournalEntry.objects.filter(debit_acc = self).order_by('date')
		credit_entries = JournalEntry.objects.filter(credit_acc = self).order_by('date')

		debit = Decimal(0)
		credit = Decimal(0)

		for e in debit_entries:
			debit += e.value
		for e in credit_entries:
			credit += e.value

		return debit - credit

class JournalEntry(models.Model):
	code = models.UUIDField(max_length = 100,
		primary_key = True, default=uuid.uuid4)
	debit_acc = models.ForeignKey('Account',
		related_name = 'debit_entry',
		verbose_name = 'debit')
	credit_acc = models.ForeignKey('Account',
		related_name = 'credit_entry',
		verbose_name = 'credit')
	debit_branch = models.ForeignKey('Branch',
		related_name = 'debit_branch', null = True,verbose_name = 'branch',
		blank = True)
	credit_branch = models.ForeignKey('Branch',
		related_name = 'credit_branch', null = True,verbose_name = 'branch',
		blank = True)
	date = models.DateField()
	currency = models.CharField(choices = CURRENCIES, max_length = 3,
		default = 'USD')
	value = models.DecimalField(decimal_places = 2,
		max_digits = 15)
	rule = models.ForeignKey('JournalEntryRule', blank = True, null = True)
	details = models.TextField(max_length = 2000, blank = True, null = True)
	approved = models.BooleanField(default = False)

	def __str__(self):
		if self.rule:
			return self.rule.name
		elif self.details:
			return self.details
		else:
			return str(self.code)

class Branch(models.Model):
	name = models.CharField(max_length = 120)

class JournalEntryRule(models.Model):
	name = models.CharField(max_length = 200)
	display_template = models.TextField(max_length = 2000,
		blank = True, null = True)

	def __str__(self):
		return "{0}".format(self.name)

	class Meta:
		verbose_name = 'Transaction Definition'
		verbose_name_plural = 'Transaction Definitions'


class JournalEntryAction(models.Model):
	rule = models.ForeignKey('JournalEntryRule')
	action = models.CharField(choices = ACTIONS, max_length = 1)
	account_type = models.ForeignKey('AccountType', null = True,
		blank = True,
		help_text = 'Choose one of account type or specific account.')
	account = models.ForeignKey('Account', verbose_name = 'Specific account',
		blank = True, null = True,
		help_text = 'Choose one of account type or specific account.')

class Journal(models.Model):
	code = models.CharField(max_length = 100,
		primary_key = True)
	name = models.CharField(max_length = 120)

class JournalCreationRule(models.Model):
	name = models.CharField(max_length = 120,
		null = True)
	include_debt_from = models.ManyToManyField('Account',
		related_name = 'debt_included',
		help_text = 'Accounts from which to extract debt entries.')
	reversed_debit_entries = models.ManyToManyField('Account',
		related_name = 'reversed_debit_entries',
		help_text = 'Reversed entries will appear on the credit side of the journal.',
		blank = True)
	include_credit_from = models.ManyToManyField('Account',
		related_name = 'credit_included',
		help_text = 'Accounts from which to extract credit entries.')
	reversed_credit_entries = models.ManyToManyField('Account',
		related_name = 'reversed_credit_entries',
		help_text = 'Reversed entries will appear on the debit side of the journal.',
		blank = True)
	multi_column = models.BooleanField(default = False)
	latest_pdf = models.FileField(upload_to ='journal_pdfs', null = True)

	class Meta:
		verbose_name = 'Posting Rule'
		verbose_name_plural = 'Posting Rules'

	def __str__(self):
		return self.name
