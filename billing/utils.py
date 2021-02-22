import copy

from celery import current_app
from celery.schedules import crontab

from books.models import BillingMethod
from books.tasks.billing import update_billing_status

def init_billing_system():
    """ Initialize the billing system when the server boots. """
    
    billing_methods = BillingMethod.objects.all()

    # Make sure all the default BillingMethods are present
    if len(billing_methods) == 0:
        default_method_kwargs = {'time':'05:00', 'day_of_month':1, 'grace_period':14}
        default_billing_periods = {'Monthly':1, 'Quarterly':3, 'Biannual':6, 'Annual':12}

        # Create each of the default billing methods
        for method_description, billing_period in  default_billing_periods.items():
            method_kwargs = copy.copy(default_method_kwargs)
            method_kwargs['description'] = method_description
            method_kwargs['billing_period'] = billing_period
            method_obj = BillingMethod.objects.create(**method_kwargs)    
    else:
        for method_obj in billing_methods:
            bind_periodic_update_task(method_obj) # Add periodic task to celery

def bind_periodic_update_task(billing_method):
    """ Add the periodic task to the currently running celery instance. """

    split_time = str(billing_method.time).split(':')
    hour = split_time[0]
    minute = split_time[1]
    current_app.add_periodic_task(
        crontab(hour=hour, minute=minute, day_of_month=billing_method.day_of_month,
            month_of_year=f"*/{billing_method.billing_period}"),
        update_billing_status.s(billing_method.pk), expires = 300)