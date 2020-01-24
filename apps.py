import sys
from django.apps import AppConfig, apps
from django.db.utils import ProgrammingError

TESTING = 'test' in sys.argv


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        from books import listeners
        from django.conf import settings
        bootstrap_system()


        

def bootstrap_system():
    from django.conf import settings
    from django.contrib.auth.models import Group

    try:
        # Create all the system user groups
        Group.objects.get_or_create(name = settings.OPEXA_BOOKS_ADMIN_USER_GROUP_NAME)
        Group.objects.get_or_create(name = settings.OPEXA_BOOKS_STANDARD_USER_GROUP_NAME)
    except :
        pass
