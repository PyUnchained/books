from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.db.models import Q

from books.models import Account, AccountGroup, DoubleEntry
from books.utils.auth import get_internal_system_account


class AccountModelTestCase(TestCase):

    def test_account_output(self):
        system_account = get_internal_system_account()

        known_account_groups = {}
        for ag in AccountGroup.objects.filter(system_account = system_account):
            known_account_groups[ag.name] = ag

        bank_acc = Account.objects.create(code = 1000, name = 'Bank',
            system_account = system_account,
            account_group = known_account_groups['current assets'])

        loans_acc = Account.objects.create(code = 2600, name = 'Working Capital Loans',
            system_account = system_account,
            account_group = known_account_groups['long-term liabilities'])

        loan_date = timezone.now().date()-timedelta(days = 30)
        debits = [{"account" :bank_acc, "value": 5000}]
        credits = [{"account" :loans_acc, "value": 5000}]
        DoubleEntry.record(debits= debits, credits = credits,
            date = loan_date, system_account = system_account, details = 'Initial Loan')

        bank_acc = Account.objects.get(code = 1000)
        bank_acc.as_dict()
        bank_acc.as_t()
        bank_acc.as_pdf()
        bank_acc.save()