import traceback

from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Q

from books.signals.api_signals import double_entry_sig,create_account_sig
from books.tasks import create_account

from .models import SingleEntry, Account, AccountGroup, SystemAccount, SystemUser


@receiver(post_delete, sender=SystemAccount)
def delete_associated_users_hook(sender, instance, using, **kwargs):
    #Make sure any users without accounts are also deleted
    SystemUser.objects.filter(account = None,
        is_superuser = False).delete()