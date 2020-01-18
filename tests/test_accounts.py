from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.db.models import Q

from books.models import Account, AccountGroup, SingleEntry

from books.utils.auth import register_new_account
from books.apps import bootstrap_system

# Create your tests here.
class AccountModelTestCase(TestCase):

    def setUp(self):
        bootstrap_system()
        account_dict = {'name':'Flimox', 'password':'pandas',
        'email':'n4g8jgt@mail.com'}
        new_account = register_new_account(**account_dict)

        bank_acc = Account.objects.get(code = 1000)
        bank_acc_2 = Account.objects.create(name = 'Secondary Bank Account',
            parent = bank_acc, code = 1001, system_account = bank_acc.system_account)
        petty_cash_acc = Account.objects.get(code = 1030)
        loans_acc = Account.objects.get(code = 2600)
        equipment_acc = Account.objects.get(code = 1840)
        payroll_payable = Account.objects.get(code = 2200)
        payroll_expense_acc = Account.objects.get(code = 5220)
        payroll_tax_payable = Account.objects.get(code =2260)
        # test_accs = [bank_acc, bank_acc_2, petty_cash_acc, loans_acc, equipment_acc]

        # Take out 5000 dollar loan 1 month prior
        loan_date = timezone.now().date()-timedelta(days = 30)
        SingleEntry.objects.create(account = bank_acc, action = 'D',
            value = 5000, details = 'Initial Loan', date = loan_date,
            system_account = new_account)
        SingleEntry.objects.create(account = loans_acc, action = 'C',
            value = 5000, details = 'Initial Loan', date = loan_date,
            system_account = new_account)

        # Move 2000 into the secondary bank account 5 days later
        entry_date = loan_date + timedelta(days = 5)
        SingleEntry.objects.create(account = bank_acc, action = 'C',
            value = 2000, details = 'Bank Transfer', date = entry_date,
            system_account = new_account)
        SingleEntry.objects.create(account = bank_acc_2, action = 'D',
            value = 2000, details = 'Bank Transfer', date = entry_date,
            system_account = new_account)

        # Purchase 1000 equipment on same day as previous
        entry_date = loan_date + timedelta(days = 5)
        SingleEntry.objects.create(account = equipment_acc, action = 'D',
            value = 1000, details = 'Equipment Purchase', date = entry_date,
            system_account = new_account)
        SingleEntry.objects.create(account = bank_acc, action = 'C',
            value = 1000, details = 'Equipment Purchase', date = entry_date,
            system_account = new_account)

        #Pay 1500 wages at the end of the month at 9.67% Tax rate
        #First, gross pay and withholding entry
        start_of_wage_period = loan_date
        pay_day = loan_date + timedelta(days = 30)
        tax_amount = Decimal('145.05')
        net_payable_amt = Decimal('1354.95')
        SingleEntry.objects.create(account = payroll_expense_acc, action = 'D',
            value = 1500, details = 'First Month Wages', date = start_of_wage_period,
            system_account = new_account)
        SingleEntry.objects.create(account = payroll_tax_payable, action = 'C',
            value = tax_amount, details = 'First Month Wages', date = start_of_wage_period,
            system_account = new_account)
        SingleEntry.objects.create(account = payroll_payable, action = 'C',
            value = net_payable_amt, details = 'First Month Wages', date = start_of_wage_period,
            system_account = new_account)


        #Net Pay on Payday
        SingleEntry.objects.create(account = payroll_payable, action = 'D',
            value = net_payable_amt, details = 'First Month Payday',
            date = pay_day, system_account = new_account)
        SingleEntry.objects.create(account = bank_acc_2, action = 'C',
            value = net_payable_amt, details = 'First Month Payday',
            date = pay_day, system_account = new_account)

        #Tax payment on Payday
        SingleEntry.objects.create(account = payroll_tax_payable, action = 'D',
            value = tax_amount, details = 'First Month Wages TAX',
            date = pay_day, system_account = new_account)
        SingleEntry.objects.create(account = bank_acc_2, action = 'C',
            value = tax_amount, details = 'First Month Wages TAX',
            date = pay_day, system_account = new_account)

    def test_account_output(self):
        bank_acc = Account.objects.get(code = 1000)
        bank_acc.as_dict()
        bank_acc.as_t()
        bank_acc.as_pdf()