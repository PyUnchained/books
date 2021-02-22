from pathlib import Path

from django.apps import AppConfig, apps
from django.db.utils import ProgrammingError


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        from books import listeners as books_listeners
        from books.billing import listeners as billing_listeners
        from django.conf import settings
        from books.billing.utils import init_billing_system
        bootstrap_system()
        init_billing_system()
        out_path = Path(settings.BASE_DIR).joinpath('tmp')
        out_path.mkdir(exist_ok=True) #Create tmp directory

def bootstrap_system():
    from django.contrib.auth.models import Group
    import books.settings as books_settings
    from books.models import Account
    from books.utils.auth import create_default_account

    #Only run all this if there aren't any accounts already in the db.
    try:
        if Account.objects.all().count() <= 0:
            try:
                # Create all the system user groups
                Group.objects.get_or_create(name = books_settings.OPEXA_BOOKS_ADMIN_USER_GROUP_NAME)
                Group.objects.get_or_create(name = books_settings.OPEXA_BOOKS_STANDARD_USER_GROUP_NAME)

                #Create default accounting package account
                create_default_account()
            except :
                pass
    except ProgrammingError:
        pass
