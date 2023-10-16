from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from books.models import SystemAccount, AccountSettings, Account
from books.utils.auth import register_new_account
from books.forms.auth import AccountRegistrationForm
from books.apps import bootstrap_system

# Create your tests here.
class UtilsTestCase(TestCase):

    # def setUp(self):
    #     bootstrap_system()

    def test_register_new_account(self):
        #Test creating an account from a dict...
        created_user = User.objects.create_user('ot1', 'ou@mail.com', '1')
        acc_kwargs = {'name':'TestyReggy', 'email':'nat@mail.com'}
        sys_acc_1 = register_new_account(user = created_user, **acc_kwargs)

        # Test that creating an account from a form works as well
        created_user2 = User.objects.create_user('ot2', 'ou@mail.com', '1')
        account_dict = {'name':'Other Reg Testing', 'password':'pandas',
        'email':'lot@mail.com', 'confirm_password':'pandas'}
        form = AccountRegistrationForm(data = account_dict)
        sys_acc_2 = register_new_account(user = created_user2, form = form)

        #Test that there's a chart of accounts for both users
        expected_account_number = 85
        self.assertEqual(Account.objects.filter(system_account = sys_acc_1).count(),
            expected_account_number)
        self.assertEqual(Account.objects.filter(system_account = sys_acc_2).count(),
            expected_account_number)
