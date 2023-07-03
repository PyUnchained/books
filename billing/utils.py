import copy

from django.db.utils import ProgrammingError

from books.models import BillingMethod, Account, DoubleEntry
from books.utils import get_internal_system_account

def init_billing_system():
    """ Initialize the billing system when the server boots. """
    
    try:
        methods_exist = BillingMethod.objects.all().exists()

        # Make sure all the default BillingMethods are present
        if not methods_exist:
            default_method_kwargs = {'grace_period':14}
            default_billing_periods = {'Monthly':1, 'Quarterly':3, 'Biannual':6, 'Annual':12}

            # Create each of the default billing methods
            for method_description, billing_period in  default_billing_periods.items():
                method_kwargs = copy.copy(default_method_kwargs)
                method_kwargs['description'] = method_description
                method_kwargs['billing_period'] = billing_period
                method_obj = BillingMethod.objects.create(**method_kwargs)

    # Means the DB probably hasn't been set up yet
    except ProgrammingError:
        pass

def record_payment(user, **kwargs):

    for required in ['value', 'date']:
        if kwargs.get(required, None) == None:
            raise ValueError(f"Required value missing from kwargs: {required}")

    central_account = get_internal_system_account()
    if not kwargs.get('debit_acc', None):
        kwargs['debit_acc'] = central_account.get_account(code = "1000")

    if not kwargs.get('details', None):
        kwargs['details'] = f"{user} Subscription Fee."

    user_accounts_receivable = Account.objects.get(code = f"1200 - {user.username}")
    debit_entry = {'account':kwargs['debit_acc'], 'value':kwargs['value']}
    credit_entry = {'account':user_accounts_receivable, 'value':kwargs['value']}
    double_entry_dict = {'debits':[debit_entry], 'credits': [credit_entry],
        'details': kwargs['details'],
        'date':kwargs['date'], 'system_account':central_account}
    DoubleEntry.record(**double_entry_dict)