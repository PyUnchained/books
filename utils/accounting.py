from books.models import Account

def get_account(system_account, **account_kwargs):
    return Account.objects.get(system_account = system_account,
        **account_kwargs)
