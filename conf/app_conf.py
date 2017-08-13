import os

from django.db.utils import IntegrityError
from django.db.models import Q

from openpyxl import load_workbook

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS

def initial_account_types():
    """Makes sure all of the initial account types exist."""
    from books.models import AccountType

    #Create all the default account types if they don't exist already
    existing_types = AccountType.objects.all()
    for acc_choice in ACC_CHOICES:
        choice = acc_choice[1]
        choice_found = False

        for t in existing_types:
            if t.name == choice:
                choice_found = True

        if not choice_found:
            AccountType.objects.create(name = choice)

def chart_of_accounts_setup():

    from django.conf import settings
    from books.models import Account, AccountType, AccountSubType

    try:
        ACTIVE_BOOKS_PACKAGE = settings.ACTIVE_BOOKS_PACKAGE
    except:
        ACTIVE_BOOKS_PACKAGE = 'book_keeping'

    COA_FILE_PATH = os.path.join(settings.BASE_DIR, 'books/conf/coa.xlsx')
    coa_wb = load_workbook(COA_FILE_PATH)
    all_sub_types = []
    all_types = []
    for n, rec in enumerate(coa_wb['book_keeping']):
        if n > 0:
            at, created = AccountType.objects.get_or_create(
                name = rec[3].value.lower())
            st, created = AccountSubType.objects.get_or_create(
                name =rec[4].value.lower())

            account_data = {'name' : rec[0].value.title(),
            'code' : rec[1].value,
            'account_type': at,
            'sub_type':st}

            if st not in all_sub_types:
                all_sub_types.append(st)
            if at not in all_types:
                all_types.append(at)

            try:
                Account.objects.get_or_create(**account_data)

            #If the code already exists, but other details
            #have been changed in the coa excel file
            except IntegrityError:
                code = account_data.pop('code')
                Account.objects.update_or_create(
                        code=code, defaults=account_data
                )

    AccountType.objects.filter(~Q(name__in = all_types)).delete()
    AccountSubType.objects.filter(~Q(name__in = all_sub_types)).delete()