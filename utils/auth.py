from django.conf import settings
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils import timezone
from django.apps import apps

from .accounting import chart_of_accounts_setup
from books.models import SystemAccount, AccountSettings


def register_new_account(user = None, form = None, *args, **system_acc_kwargs):
    """ Registers a new system account.

    One of either 'form' or 'system_acc_kwargs' is required. If the user already
    has an account, their existing account is returned

    Parameters
    ----------

    user: User object
    form: ModelForm, optional.
    system_acc_kwargs : Kwargs dict, optional.

    Returns
    -------

    The user's account in the bookkeeping system

    Raises
    ------

    ValueError - Raised when no user kwarg is supplied
    
    """

    if not user:
        raise ValueError('User instance missing from kwargs.')

    other_accs = user.systemaccount_set.all()
    account_already_registered = other_accs.count() > 0
    if account_already_registered:
        return other_accs[0]

    if form:
        account = form.save(commit = False)
    else:
        account = SystemAccount(**system_acc_kwargs)

    with transaction.atomic():
        account.settings = AccountSettings.objects.create(
            financial_year_start = timezone.now().date())
        account.save()
        account.users.add(user)
        chart_of_accounts_setup(account, skip_is_test = True)
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
        g = Group.objects.get(name = settings.BOOKS_ADMIN_USER_GROUP_NAME)
        admin_user.groups.add(g)

        return admin_user

def get_account_for_user(user):
    try:
        return user.systemaccount_set.all()[0]
    except SystemAccount.DoesNotExist:
        return None