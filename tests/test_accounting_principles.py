from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from books.models import Account, AccountGroup, SingleEntry, SystemAccount
from books.utils.auth import get_default_account
from books.apps import bootstrap_system
from books.financial_statements.trial_balance import TrialBalance

# Create your tests here.
class AccountingPrinciplesTestCase(TestCase):

	def setUp(self):
	    bootstrap_system()
	    self.new_account = get_default_account()

	    bank_acc = Account.objects.get(code = 1000)
	    bank_acc_2 = Account.objects.get(code = 1001)
	    petty_cash_acc = Account.objects.get(code = 1030)
	    loans_acc = Account.objects.get(code = 2600)
	    equipment_acc = Account.objects.get(code = 1840)
	    payroll_payable = Account.objects.get(code = 2200)
	    payroll_expense_acc = Account.objects.get(code = 5220)
	    payroll_tax_payable = Account.objects.get(code =2260)

	    # Take out 5000 dollar loan 1 month prior
	    loan_date = timezone.now().date()-timedelta(days = 30)
	    SingleEntry.objects.create(account = bank_acc, action = 'D',
	        value = 5000, details = 'Initial Loan', date = loan_date,
	        system_account = self.new_account)
	    SingleEntry.objects.create(account = loans_acc, action = 'C',
	        value = 5000, details = 'Initial Loan', date = loan_date,
	        system_account = self.new_account)

	    # Move 2000 into the secondary bank account 5 days later
	    entry_date = loan_date + timedelta(days = 5)
	    SingleEntry.objects.create(account = bank_acc, action = 'C',
	        value = 2000, details = 'Bank Transfer', date = entry_date,
	        system_account = self.new_account)
	    SingleEntry.objects.create(account = bank_acc_2, action = 'D',
	        value = 2000, details = 'Bank Transfer', date = entry_date,
	        system_account = self.new_account)

	    # Purchase 1000 equipment on same day as previous
	    entry_date = loan_date + timedelta(days = 5)
	    SingleEntry.objects.create(account = equipment_acc, action = 'D',
	        value = 1000, details = 'Equipment Purchase', date = entry_date,
	        system_account = self.new_account)
	    SingleEntry.objects.create(account = bank_acc, action = 'C',
	        value = 1000, details = 'Equipment Purchase', date = entry_date,
	        system_account = self.new_account)

	    #Pay 1500 wages at the end of the month at 9.67% Tax rate
	    #First, gross pay and withholding entry
	    start_of_wage_period = loan_date
	    pay_day = loan_date + timedelta(days = 30)
	    tax_amount = Decimal('145.05')
	    net_payable_amt = Decimal('1354.95')
	    SingleEntry.objects.create(account = payroll_expense_acc, action = 'D',
	        value = 1500, details = 'First Month Wages', date = start_of_wage_period,
	        system_account = self.new_account)
	    SingleEntry.objects.create(account = payroll_tax_payable, action = 'C',
	        value = tax_amount, details = 'First Month Wages', date = start_of_wage_period,
	        system_account = self.new_account)
	    SingleEntry.objects.create(account = payroll_payable, action = 'C',
	        value = net_payable_amt, details = 'First Month Wages', date = start_of_wage_period,
	        system_account = self.new_account)


	    #Net Pay on Payday
	    SingleEntry.objects.create(account = payroll_payable, action = 'D',
	        value = net_payable_amt, details = 'First Month Payday',
	        date = pay_day, system_account = self.new_account)
	    SingleEntry.objects.create(account = bank_acc_2, action = 'C',
	        value = net_payable_amt, details = 'First Month Payday',
	        date = pay_day, system_account = self.new_account)

	    #Tax payment on Payday
	    SingleEntry.objects.create(account = payroll_tax_payable, action = 'D',
	        value = tax_amount, details = 'First Month Wages TAX',
	        date = pay_day, system_account = self.new_account)
	    SingleEntry.objects.create(account = bank_acc_2, action = 'C',
	        value = tax_amount, details = 'First Month Wages TAX',
	        date = pay_day, system_account = self.new_account)


	def test_account_balances(self):
		"""
		The system needs to be able to correctly total accounts, including their child accounts, and here
		is where we set that up.
		"""
		bank_acc = Account.objects.get(code = 1000)
		bank_acc_2 = Account.objects.get(code = 1001)
		petty_cash_acc = Account.objects.get(code = 1030)
		loans_acc = Account.objects.get(code = 2600)
		equipment_acc = Account.objects.get(code = 1840)
		payroll_payable = Account.objects.get(code = 2200)
		payroll_expense_acc = Account.objects.get(code = 5220)
		payroll_tax_payable = Account.objects.get(code =2260)
		self.assertEqual(bank_acc.balance(), Decimal(2000.00))
		self.assertEqual(bank_acc_2.balance(), Decimal(500.00))
		self.assertEqual(petty_cash_acc.balance(), Decimal(0.00))
		self.assertEqual(loans_acc.balance(), Decimal(5000.00))
		self.assertEqual(equipment_acc.balance(), Decimal(1000.00))
		self.assertEqual(payroll_payable.balance(), Decimal('0.00'))
		self.assertEqual(payroll_expense_acc.balance(), Decimal(1500))
		self.assertEqual(payroll_tax_payable.balance(), Decimal('0.00'))

	def test_trial_balance(self):
		end_of_month = timezone.now().date() + timedelta(days = 60)
		tb = TrialBalance(self.new_account)
		tb_dict = tb.as_dict()
		tb.as_pdf(month = end_of_month.month, year=end_of_month.year,
			file_name = 'test_tb.pdf')
		self.assertEqual(tb_dict['debit_total'], tb_dict['credit_total'])
		self.assertEqual(tb_dict['debit_total'], Decimal('5000'))

