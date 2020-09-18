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

    def setUp(self):
        bootstrap_system()

    def test_register_new_account(self):
        #Test creating an account from a dict...
        account_dict = {'name':'TestyReggy', 'password':'pandas',
        'email':'nat@mail.com'}
        new_account = register_new_account(**account_dict)

        created_user = User.objects.get(username = 'nat@mail.com')
        self.assertEqual(created_user.username, account_dict['email'])

        #make sure account password was correctly hashed
        password_hashed = 'pbkdf2_sha256' in new_account.password
        self.assertTrue(password_hashed)


        # Test that creating an account from a form works as well
        account_dict = {'name':'Other Reg Testing', 'password':'pandas',
        'email':'lot@mail.com', 'confirm_password':'pandas'}
        form = AccountRegistrationForm(data = account_dict)
        new_account = register_new_account(form = form)

        created_user = User.objects.get(username = 'lot@mail.com')
        self.assertEqual(created_user.username, account_dict['email'])

        #make sure account password was correctly hashed
        password_hashed = 'pbkdf2_sha256' in new_account.password
        self.assertTrue(password_hashed)

        #Test that there's a chart of accounts for both users
        sys_acc_1 = SystemAccount.objects.get(email = 'nat@mail.com')
        sys_acc_2 = SystemAccount.objects.get(email = 'lot@mail.com')
        self.assertEqual(Account.objects.filter(system_account = sys_acc_1).count(),
            78)
        self.assertEqual(Account.objects.filter(system_account = sys_acc_1).count(),
            Account.objects.filter(system_account = sys_acc_2).count())
