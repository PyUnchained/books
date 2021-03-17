import os

from django.db.utils import IntegrityError
from django.db.models import Q
from django.db import transaction
from django.conf import settings

from openpyxl import load_workbook

from books.models import (Account, AccountGroup, SystemAccount, AccountSettings, Invoice,
    DoubleEntry)
from .runtime import is_celery, is_test

LAST_KNOWN_SYSTEM_ACCOUNT = None

def chart_of_accounts_setup(system_account, skip_is_test = False):

    # None of this matters to the celery worker, since the web app will create
    # all this in the db
    if is_celery():
        return

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
                name = parent_name, system_account = system_account)

            try:
                acc_group, acc_created = AccountGroup.objects.get_or_create(
                    name =acc_group_name, parent = parent_group,
                    system_account = system_account)
                
            #If the Sub-group is the same as one of the root parent account groups,
            #an error gets thrown, since an account with that name already exists, so we don't
            # need to do anythin else
            except IntegrityError:
                pass


    # If this is inside a test, we won't need the full chart of accounts
    if not skip_is_test:
        if is_test():
            return

    for n, rec in enumerate(coa_wb['book_keeping']):
        if n > 0:
            acc_group_name = rec[4].value.lower().strip()
            acc_group = AccountGroup.objects.get(name =acc_group_name,
                system_account = system_account)

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

def get_account(system_account, **account_kwargs):
    return Account.objects.get(system_account = system_account,
        **account_kwargs)


def create_default_account():
    with transaction.atomic():
        system_acc, created = SystemAccount.objects.get_or_create(name = "opexa_books")
        if created:
            system_acc_settings = AccountSettings.objects.create(financial_year_start = timezone.now().date())
            system_acc.settings = system_acc_settings
            system_acc.save()
            chart_of_accounts_setup(system_acc)
    return system_acc

def get_internal_system_account():
    global LAST_KNOWN_SYSTEM_ACCOUNT

    try:
        LAST_KNOWN_SYSTEM_ACCOUNT = SystemAccount.objects.get(name = "opexa_books")
    except SystemAccount.DoesNotExist:
        LAST_KNOWN_SYSTEM_ACCOUNT = create_default_account()

    except SystemAccount.MultipleObjectsReturned:
        accs = SystemAccount.objects.filter(name = "opexa_books")
        chosen_acc = accs[0]
        for a in accs[1:]:
            a.delete()
        LAST_KNOWN_SYSTEM_ACCOUNT = chosen_acc

    return LAST_KNOWN_SYSTEM_ACCOUNT

def invoice_user(user, date = None, due = None, system_account = None, invoice_entries =[],
    associated_billing_accounts = [], account_info = None, sales_account = None, *kwargs):

    if not system_account:
        system_account = get_internal_system_account()
    
    with transaction.atomic():
        invoice = Invoice.objects.create(
            due = due, date = date,
            entries = invoice_entries)

        # If there are any associated billing accounts, link them to the invoice
        for acc in associated_billing_accounts:
            acc.save()
            invoice.billing_accounts.add(acc)

        if not account_info:
            account = system_account.get_account(code = f'1200 - {user.username}')
            balance = account.balance(as_at = date)
            account_info = (account, balance)

        if not sales_account:
            sales_account = system_account.get_account(code = '4000')

        # Create double entry records for all items on the invoice
        for entry in invoice_entries:
            debit_entry = {'account':account_info[0], 'value':entry['total']}
            credit_entry = {'account':sales_account, 'value':entry['total']}
            double_entry_dict = {'debits':[debit_entry], 'credits': [credit_entry],
                'details': entry['description'], 'date':date,
                'system_account':system_account}
            de = DoubleEntry.record(**double_entry_dict)

    return invoice

def invoice_user_from_bill(*args, **kwargs):
    """ Used when generating an invoice from a spefified list of charges 
    resulting from a BillingAccount payment being charged. """

    invoice_entries = []
    associated_billing_accounts = []
    for account_charge in kwargs.pop('account_charges', []):
        associated_billing_accounts.append(account_charge['billing_account'])
        invoice_entry = generate_invoice_entry(
            billing_account = account_charge['billing_account'],
            quantity = account_charge['quantity'],
            unit_price = account_charge['billing_account'].billing_tier.unit_price)
        invoice_entries.append(invoice_entry)

    kwargs['associated_billing_accounts'] = associated_billing_accounts
    kwargs['invoice_entries'] = invoice_entries
    return invoice_user(*args, **kwargs)


def generate_invoice_entry(description = None, billing_account = None,
    **kwargs):

    """ Generate a dict, representing a single invoice entry, formatted to be
    Json serializable. """

    required_kwargs = ['quantity', 'unit_price']
    for k in required_kwargs:
        if k not in kwargs:
            raise ValueError(f'Required keyword argument missing: {k}')

    total = kwargs['quantity']*kwargs['unit_price']
    if billing_account:
        billing_account_pk = billing_account.pk

        # Set default description if none given
        if not description:
            description = f"{billing_account.product_description}"

    # Json rerializable response
    resp_dict = {'total':float(total), 'billing_account':billing_account_pk,
        'description':description, 'quantity':int(kwargs['quantity']),
        'unit_price':float(kwargs['unit_price'])}
    return resp_dict