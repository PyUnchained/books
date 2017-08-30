from django.apps import AppConfig, apps

from books.conf.app_conf import initial_account_types, chart_of_accounts_setup, migrate_to_single_entry


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'bookkeeping'

    def ready(self, *args, **kwargs):
        import books.listeners
        try:
            initial_account_types()
        except:
            pass

        try:
            chart_of_accounts_setup()
        except:
            print ('\n\nWARNING: An error occured attempting to create standard chart of accounts.\n\n')

        # try:
        # migrate_to_single_entry()
        # except:
        #     print ('\n\nWARNING: An error occured attempting to migrate to single entries.\n\n')
        
                


