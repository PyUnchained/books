import sys
from django.apps import AppConfig, apps

TESTING = 'test' in sys.argv

class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        pass

