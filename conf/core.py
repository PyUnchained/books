import os

from django.db.utils import IntegrityError
from django.db.models import Q
from django.conf import settings

from openpyxl import load_workbook

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS

def chart_of_accounts_setup(system_account):

    from django.conf import settings
    from books.models import Account, AccountGroup

    try:
        ACTIVE_BOOKS_PACKAGE = settings.ACTIVE_BOOKS_PACKAGE
    except:
        ACTIVE_BOOKS_PACKAGE = 'book_keeping'

    COA_FILE_PATH = os.path.join(settings.BASE_DIR, 'books/conf/coa.xlsx')
    coa_wb = load_workbook(COA_FILE_PATH)
    all_sub_types = []
    all_types = []

    #Create all the necessary root account groups and their children.
    for n, rec in enumerate(coa_wb['book_keeping']):
        if n > 0:
            parent_name = rec[3].value.lower().strip()
            acc_group_name = rec[4].value.lower().strip()

            parent_group, created = AccountGroup.objects.get_or_create(
                name = parent_name)

            try:
                acc_group, acc_created = AccountGroup.objects.get_or_create(
                    name =acc_group_name, parent = parent_group)
                
            #If the Sub-group is the same as one of the root parent account groups,
            #an error gets thrown, since an account with that name already exists, so we don't
            # need to do anythin else
            except IntegrityError:
                pass

    for n, rec in enumerate(coa_wb['book_keeping']):
        if n > 0:
            acc_group_name = rec[4].value.lower().strip()
            acc_group = AccountGroup.objects.get(name =acc_group_name)

            account_data = {'name' : rec[0].value.title(),
            'code' : rec[1].value,
            'account_group': acc_group,
            'system_account':system_account}

            try:
                Account.objects.get_or_create(**account_data)

            #If the code already exists, but other details
            #have been changed in the coa excel file
            except IntegrityError:
                code = account_data.pop('code')
                Account.objects.update_or_create(
                        code=code, defaults=account_data
                )