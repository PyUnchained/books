from django.test import TestCase

from books.models import Account, JournalCreationRule
from books.conf.app_conf import chart_of_accounts_setup

from books.virtual.journal import VirtualJournal

# Create your tests here.
class VirtualJournalTestCase(TestCase):

	fixtures = ['books']

	# def setUp(self):
	# 	chart_of_accounts_setup()

	def test_trial_balance(self):
		#Trial Balance
		vj = VirtualJournal(
			JournalCreationRule.objects.get(preset = 'TB'))
	def test_cash_book(self):
		vj = VirtualJournal(
			JournalCreationRule.objects.get(preset = 'CB'))

	def test_balance_sheet(self):
		vj = VirtualJournal(
			JournalCreationRule.objects.get(preset = 'BS'))

	def test_profit_and_loss(self):
		vj = VirtualJournal(
			JournalCreationRule.objects.get(preset = 'PL'))
