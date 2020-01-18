from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse_lazy, reverse
from django.forms.widgets import PasswordInput

from books.models import Account, AccountGroup, SystemAccount, SystemUser
from books.forms.auth import AccountRegistrationForm, LoginForm
from books.apps import bootstrap_system
from books.utils.auth import register_new_account

# Create your tests here.
class AuthTestCase(TestCase):

    def setUp(self):
        bootstrap_system()
        account_dict = {'name':'AuthTestCase', 'password':'pandasforte3',
        'email':'AuthTestCase@mail.com'}
        self.new_account = register_new_account(**account_dict)

    def test_registration_form(self):

        reg_form_data = {'name': 'tk', 'email': 'f@mail.com', 'password': '123',
        'confirm_password': '123'}
        reg_form = AccountRegistrationForm(data = reg_form_data)
        self.assertTrue(reg_form.is_valid())

        
        for f in reg_form.fields:
            #Make sure all fields are required
            self.assertTrue(reg_form.fields[f].required)

            #Make the password fields have the correct widget set
            if 'password' in f:
                self.assertTrue(isinstance(reg_form.fields[f].widget, PasswordInput))

        # Make sure mismatched passwords are caught
        reg_form_data = {'name': 'tk', 'email': 'tw@mail.com', 'password': '123',
        'confirm_password': '1rgrgrg23'}
        reg_form = AccountRegistrationForm(data = reg_form_data)
        self.assertFalse(reg_form.is_valid())

    def test_login_form(self):
        form_data = {'email':'this@main.com', 'password':'hooga'}
        form = LoginForm(data = form_data)
        self.assertTrue(form.is_valid())

    def test_login_view(self):

        # If the user's account has not had all the initial sources of capital/expenses/liabilities
        # input, site should redirect to the 'capital_sources' view
        client = Client()
        post_dict = {'email': 'AuthTestCase@mail.com', 'password': 'pandasforte3'}        
        response = client.post(reverse('opexa_books:login'), post_dict,
            follow = True)
        self.assertEqual(response.resolver_match.url_name, 'capital_sources')
        self.assertEqual(response.redirect_chain[0][1], 302)

        #If inital declarations have been done, site should instead redirect to the dashboard
        self.new_account.initial_setup_done = True
        self.new_account.save()
        
        client = Client()
        post_dict = {'email': 'AuthTestCase@mail.com', 'password': 'pandasforte3'}        
        response = client.post(reverse('opexa_books:login'), post_dict,
            follow = True)
        self.assertEqual(response.resolver_match.url_name, 'dashboard')
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_signup_view(self):

        #Normal signup...
        client = Client()
        post_dict = {'name': 'tk', 'email': 'tw@mail.com', 'password': '123',
        'confirm_password': '123'}        
        response = client.post(reverse('opexa_books:new_account'), post_dict,
            follow = True)
        self.assertEqual(response.redirect_chain[0][1], 302)

        #Make signup fails gracefully when the email is reused
        post_dict = {'name': 'sfsfsf', 'email': 'tw@mail.com', 'password': 'sfsfsf',
        'confirm_password': 'sfsfsf'}        
        response = client.post(reverse('opexa_books:new_account'), post_dict,
            follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
