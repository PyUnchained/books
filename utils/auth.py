from django.conf import settings
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils import timezone
from django.apps import apps

from books.conf import chart_of_accounts_setup
from books.conf.settings import ADMIN_USER_GROUP_NAME
from books.models import SystemAccount, AccountSettings

def register_new_account(form = None, **kwargs):

    if form:
        account = form.save(commit = False)
    else:
        account = SystemAccount(**kwargs)

    with transaction.atomic():

        password_str = account.password
        account.password = make_password(password_str) # Hash the account password string
        account.settings = AccountSettings.objects.create(
            financial_year_start = timezone.now().date())
        account.save() 

        register_new_admin_user(account, account.email, password_str)

        #Setup initial Chart of Accounts
        chart_of_accounts_setup(account)
        return account

def register_new_admin_user(account, username, password):

    with transaction.atomic():
        app_label, model_name = settings.AUTH_USER_MODEL.split('.')
        UserModel = apps.get_model(app_label=app_label, model_name=model_name)
        admin_user = UserModel.objects.create_user(username = username,
            email = account.email, password = password,
            is_admin = True, is_staff = True)
        account.users.add(admin_user)

        #Add them to the admin user group
        g = Group.objects.get(name = ADMIN_USER_GROUP_NAME)
        admin_user.groups.add(g)

        return admin_user