from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from books.models import Account, DoubleEntry, Transaction
from books.blockchain import Blockchain

User = get_user_model()
ACTIVE = hasattr(settings, 'BLOCKCHAIN_NAME')

@receiver(post_save, sender=Account)
def new_address(sender, instance, created, raw, **kwargs):
    
    if not raw and ACTIVE:
        if created:
            instance.address_id = Blockchain.getnewaddress()
            instance.save()

@receiver(post_save, sender=DoubleEntry)
def write_to_blockchain(sender, instance, raw, **kwargs):
    
    if not raw and ACTIVE:
        if not instance.pk:
            instance.address_id = Blockchain.getnewaddress()

@receiver(post_save, sender=Transaction)
def record_double_entry_for_transaction(sender, instance, raw, **kwargs):
    if raw:
        return

    if not instance.double_entry_record:
        instance.commit()