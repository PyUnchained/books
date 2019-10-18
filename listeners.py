import traceback

from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Q

from books.signals.api_signals import double_entry_sig,create_account_sig
from books.tasks import create_account

from .models import SingleEntry, Account, AccountGroup


def create_standard_accs(name_list):
	from django.conf import settings

	for n in name_list:
		if n in settings.ACCOUNT_DEFINITIONS:
			try:
				acc_type, create = AccountGroup.objects.get_or_create(
					name = settings.ACCOUNT_DEFINITIONS[n]['account_type'],
					)
				Account.objects.get_or_create(name = n,
					account_type = acc_type,
					code = settings.ACCOUNT_DEFINITIONS[n]['code'])
			except:
				traceback.print_exc()

	


@receiver(create_account_sig)
def create_an_account(signal = None,sender =None,**kwargs):
    create_account.apply(kwargs = kwargs)

@receiver(double_entry_sig)
def record_double_entry(signal = None, **kwargs):

	create_standard_accs([kwargs.get('debit_acc'),
		kwargs.get('credit_acc')])

	#Make the debit entry
	debit_acc = Account.objects.get(name = kwargs.get('debit_acc'))
	debit = SingleEntry.objects.create(date = kwargs.get('date'),
		account = debit_acc, action = 'D',
		value = kwargs.get('value'),
		details = kwargs.get('debit_details')
		)

	#Make the credit entry
	credit_acc = Account.objects.get(name = kwargs.get('credit_acc'))
	credit = SingleEntry.objects.create(date = kwargs.get('date'),
		account = credit_acc, action = 'C',
		value = kwargs.get('value'),
		details = kwargs.get('credit_details'))

