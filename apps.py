from pathlib import Path

from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django.conf import settings

from books.conf import app_settings


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
    from books.models import Account
    from books.utils.auth import create_default_account

    try:
        if Account.objects.all().count() <= 0:
            try:
                create_default_account()
            except :
                pass

    # Means the DB isn't ready yet
    except ProgrammingError:
        pass
