from django.test import TestCase

from books.models.billing import BillingMethod
from books.billing.utils import init_billing_system
from books.tasks.billing import update_billing_status

# Create your tests here.
class BillingInitializationTestCase(TestCase):

    def setUp(self):
        init_billing_system()

    def test_billing_cycle(self):
        billing_method = BillingMethod.objects.get(description = 'Monthly')
        update_billing_status(billing_method.pk)