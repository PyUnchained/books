import sys

from django.apps import AppConfig, apps

from books.conf.app_conf import initial_account_types, chart_of_accounts_setup, migrate_to_single_entry

TESTING = 'test' in sys.argv

class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'bookkeeping'

    def ready(self, *args, **kwargs):
        import books.listeners
        if not TESTING:
            try:
                initial_account_types()
            except:
                pass

            try:
                chart_of_accounts_setup()
            except:
                print ('\n\nWARNING: An error occured attempting to create standard chart of accounts.\n\n')
        else:
            print ("Running Test: Accounts not initialized")

