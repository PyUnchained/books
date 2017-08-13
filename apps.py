from django.apps import AppConfig, apps

from books.conf.app_conf import initial_account_types, chart_of_accounts_setup


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'bookkeeping'

    def ready(self, *args, **kwargs):
        import books.listeners
        try:
            initial_account_types()
        except:
            pass
        chart_of_accounts_setup()
                


