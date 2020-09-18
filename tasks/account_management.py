import time 
import importlib
from pathlib import Path

from django.conf import settings
from celery import shared_task

from books.models import Account, AccountGroup
from books.blockchain import Blockchain

def check_required_fields(fields, dict_obj):
    not_found = []
    for f in fields:
        if f not in dict_obj:
            not_found.append(f)

    if not_found:
        error_msg = "{} not found in kwargs".format(','.join(not_found))
    else:
        return

@shared_task
def create_account(**kwargs):
    #Make sure the kwarg fields expected to be sent when this function is 
    #called are present.
    required_fields = ['name', 'account_type']
    check_required_fields(required_fields,kwargs)

    account_type_obj, created = AccountGroup.objects.get_or_create(
        name =kwargs.get('account_type'))
    name = kwargs.get('name')
    code = name
    account_kwargs = {'name' : name,
        'account_type' : account_type_obj,
        'code':code}
    acc, created = Account.objects.get_or_create(**account_kwargs)

@shared_task
def create_blockchain_address(account_pk):
    wallet_address = Blockchain.getnewaddress()
    acc = Account.objects.get(pk = account_pk)
    acc.address_id = wallet_address
    acc.save()

@shared_task
def get_or_create_admin_address():
    address_path = Path(f'~/multichain.info').expanduser()