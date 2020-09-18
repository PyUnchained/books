

from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from books.models import Account, DoubleEntry
from books.blockchain import Blockchain

@receiver(pre_save, sender=Account)
def new_address(sender, instance, raw, **kwargs):
    
    if not raw:
        if not instance.pk:
            instance.address_id = Blockchain.getnewaddress()

@receiver(post_save, sender=DoubleEntry)
def write_to_blockchain(sender, instance, raw, **kwargs):
    
    if not raw:
        if not instance.pk:
            instance.address_id = Blockchain.getnewaddress()