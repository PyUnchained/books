import json
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from django_celery_beat.models import PeriodicTask, CrontabSchedule, crontab_schedule_celery_timezone

from books.models import BillingMethod
from books.billing.utils import bind_periodic_update_task

@receiver(post_save, sender=BillingMethod)
def update_associated_periodic_task(sender, instance, created, raw, **kwargs):
    
    if raw:
        return

    if created:
        bind_periodic_update_task(instance) # Adds the a task to the celery beat scheduler