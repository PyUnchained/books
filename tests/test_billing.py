from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from books.models.billing import BillingMethod, BillingTier, BillingAccount
from books.tasks.billing import update_billing_status

User = get_user_model()


class BillingTasksTestCase(TestCase):

    fixtures = ['books/tests/basic_test_fixtures.json']

    def setUp(self):
        today = timezone.now().date()
        self.user = User.objects.get(username = 'test_user')

        # Create at least one billing method and one billing tier
        self.billing_method = BillingMethod.objects.create(description = 'Monthly')
        self.tier = BillingTier.objects.create(description = 'Entry Level',
            charge = 20.00)
        #Create a specific billing account
        self.billing_account = BillingAccount.objects.create(user = self.user,
            billing_method = self.billing_method, billing_tier = self.tier,
            start_date = today, product_description = 'Services rendered')

    def test_update_task(self):
        # When called with valid date string
        update_billing_status(self.billing_account.pk, current_date = '12/2/2000')

        # When called with an invalid date string
        with self.assertRaises(ValueError):
            update_billing_status(self.billing_account.pk, current_date = '234kmdfg')
        


class BillingCycleTestCase(TestCase):

    fixtures = ['books/tests/basic_test_fixtures.json']

    def test_billing_cycle(self):
        today = timezone.now().date()
        user = User.objects.get(username = 'test_user')

        # Create at least one billing method and one billing tier
        billing_method = BillingMethod.objects.create(description = 'Monthly')
        tier = BillingTier.objects.create(description = 'Entry Level',
            unit_price = 20.00)


        #Create a specific billing account
        acc = BillingAccount.objects.create(user = user,
            billing_method = billing_method, billing_tier = tier,
            start_date = today, last_billed = today,
            product_description = 'Services rendered')

        # First day the task runs...
        update_required = update_billing_status(acc.pk,
            current_date = today.strftime("%d/%m/%Y"))
        self.assertFalse(update_required)

        # When the task is run on the date specified by "next_billing"
        update_required = update_billing_status(acc.pk,
            current_date = acc.next_billed.strftime("%d/%m/%Y"))
        self.assertTrue(update_required)
        

        