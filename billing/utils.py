import copy

from django.db.utils import ProgrammingError
from celery import current_app
from celery.schedules import crontab

from books.models import BillingMethod
from books.tasks.billing import update_billing_status

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