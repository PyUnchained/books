import traceback

from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Q


from management.models import (Booking, RegisteredAddress, Consignment,Parcel, CompletionCode,
    ATCommand, BroadcastEvent, Offer, Driver, Client)
from management.models.signals import*
from management.dj_channels.consumers.gsm_gateway import send_text_cmd

from books.signals.api_signals import write_journal_entry_sig,create_account_sig
from books.tasks import create_account


@receiver(create_account_sig)
def create_an_account(signal = None,sender =None,**kwargs):
    create_account.apply(kwargs = kwargs)
    