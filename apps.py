from django.apps import AppConfig, apps

from books.conf.app_conf import initial_account_types

class BooksConfig(AppConfig):
    name = 'books'

    def ready(self, *args, **kwargs):
        initial_account_types()

