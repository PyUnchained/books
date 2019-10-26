import sys
from django.apps import AppConfig, apps
from django.db.utils import ProgrammingError

TESTING = 'test' in sys.argv


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        from books import hooks
        bootstrap_system()
        

def bootstrap_system():
    from books.conf.settings import ADMIN_USER_GROUP_NAME, STANDARD_USER_GROUP_NAME
    from django.contrib.auth.models import Group

    try:
        # Create all the system user groups
        Group.objects.get_or_create(name = ADMIN_USER_GROUP_NAME)
        Group.objects.get_or_create(name = STANDARD_USER_GROUP_NAME)
    except ProgrammingError:
        pass
