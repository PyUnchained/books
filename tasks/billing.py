from celery import shared_task

@shared_task
def update_billing_status(billing_method_pk):
    #Make sure the kwarg fields expected to be sent when this function is 
    #called are present.
    print ('Updating ')