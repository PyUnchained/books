from dateutil import relativedelta
from decimal import Decimal
import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from books.models import BillingMethod, BillingTier, BillingAccount, Invoice, Account, DoubleEntry
from books.tasks.billing import update_billing_status
from books.utils import get_internal_system_account
from books.billing.utils import record_payment

User = get_user_model()


class BillingTasksTestCase(TestCase):

    fixtures = ['books/tests/basic_test_fixtures.json']

    def setUp(self):
        today = timezone.now().date()
        self.user = User.objects.get(username = 'test_user')

        # Create at least one billing method and one billing tier
        self.billing_method = BillingMethod.objects.create(description = 'Monthly',
            grace_period = 14)
        self.tier = BillingTier.objects.create(description = 'Entry Level',
            unit_price = 20.00)
        #Create a specific billing account
        self.billing_account = BillingAccount.objects.create(user = self.user,
            billing_method = self.billing_method, billing_tier = self.tier,
            start_date = today, product_description = 'Services rendered')

    def test_update_task(self):
        # When called with valid date string
        update_billing_status(current_date = '12/2/2000')

        # When called with an invalid date string
        with self.assertRaises(ValueError):
            update_billing_status(current_date = '234kmdfg')

        # When called with valid date object
        update_billing_status(current_date = datetime.datetime.strptime(
            '12/2/2000','%m/%d/%Y'))
        


class BillingCycleTestCase(TestCase):

    fixtures = ['books/tests/basic_test_fixtures.json']

    def setUp(self):
        self.central_account = get_internal_system_account()
        self.sales_acc = self.central_account.get_account(code = "4000")
        self.bank = self.central_account.get_account(code = "1000")

    def test_billing_cycle(self):
        today = timezone.now().date()
        user = User.objects.get(username = 'test_user')

        # Create at least one billing method and one billing tier
        billing_method = BillingMethod.objects.create(description = 'Monthly',
            grace_period = 14)
        billing_method2 = BillingMethod.objects.create(description = 'Quarterly',
            grace_period = 30, billing_period = 3)
        tier1 = BillingTier.objects.create(description = 'Entry Level',
            unit_price = 20.00)
        tier2 = BillingTier.objects.create(description = 'More Expensive',
            unit_price = 130.00)


        #Create a specific billing account
        acc = BillingAccount.objects.create(user = user,
            billing_method = billing_method, billing_tier = tier1,
            start_date = today,
            product_description = 'Monthly')
                #Create a specific billing account
        acc2 = BillingAccount.objects.create(user = user,
            billing_method = billing_method2, billing_tier = tier2,
            start_date = today,
            product_description = 'Quarterly')

        # Verify that an Accounts Payable account has been created for the user
        user_accounts_receivable = Account.objects.get(code = f"1200 - {user.username}")
        self.assertEqual(user_accounts_receivable.name, 'Accounts Receivable - (test_user)')

        # When the task is run on the date specified by "next_billing"
        current_date =  today
        update_required = update_billing_status(current_date = current_date)
        self.assertTrue(update_required)

        # Check that each billing account has the next billing date set correctly
        for item in [acc, acc2]:
            item.refresh_from_db()
            self.assertEqual(item.last_billed, current_date)

        self.assertEqual(acc.next_billed, current_date + relativedelta.relativedelta(
            months = 1))
        self.assertEqual(acc2.next_billed, current_date + relativedelta.relativedelta(
            months = 3))



        # Check that the accounting was done correctly in the background
        self.assertEqual(('D', Decimal('150.00')), 
            user_accounts_receivable.balance(as_at = current_date, full = True))
        self.assertEqual(('C', Decimal('150.00')),
            self.sales_acc.balance(as_at = current_date, full = True))

        # Check that a new invoice was generated for the user
        invoice = Invoice.objects.latest('created')
        self.assertTrue(invoice.file != None)

        # Move forward past the expiry of the grace period
        grace_period_expired_date = current_date + relativedelta.relativedelta(days = 15)
        update_required = update_billing_status(
            current_date = grace_period_expired_date)
        self.assertFalse(update_required)

        # Monthly billing account should now be inactive due to the grace period,
        # but the Quarterly billing account should still be active
        for item in [acc, acc2]:
            item.refresh_from_db()
        self.assertFalse(acc.active)
        self.assertTrue(acc2.active)

        # Record a transaction representing the payment of the user's outstanding accounts.
        # Include $50 extra
        record_payment(user, value = Decimal('200.00'), debit_acc = self.bank,
            date = current_date)

        # Updating the billing status on the same day should result in all the user's
        # inactive Billing accounts being reactivated
        update_required = update_billing_status(current_date = current_date)
        self.assertFalse(update_required)

        for item in [acc, acc2]:
            item.refresh_from_db()
            self.assertTrue(item.active)

        # Move forward month since last billing
        current_date = current_date + relativedelta.relativedelta(months = 1)
        update_required = update_billing_status(current_date = current_date)

        # Should be $30 negative balance
        self.assertEqual(user_accounts_receivable.balance(as_at = current_date),
            Decimal("-30.00"))

        # Move forward till next quarterly bill should be charged
        current_date = current_date + relativedelta.relativedelta(months = 2)
        update_required = update_billing_status(current_date = current_date)
        self.assertEqual(user_accounts_receivable.balance(as_at = current_date),
            Decimal('140'))

        for item in [acc, acc2]:
            item.refresh_from_db()
            self.assertTrue(item.active)

        

        