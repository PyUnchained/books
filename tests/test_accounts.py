from django.test import TestCase

from books.models import Account, AccountGroup

from books.conf.app_conf import chart_of_accounts_setup

# Create your tests here.
class AccountModelTestCase(TestCase):

	def setUp(self):
		chart_of_accounts_setup()

	def test_chart_of_accounts_setup(self):
		self.assertEqual(Account.objects.all().count(), 81)
		self.assertEqual(AccountGroup.objects.all().count(), 27)