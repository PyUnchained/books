from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django.conf import settings

from books.conf import app_settings



class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        # Add listerners
        from books import listeners as books_listeners
        from books.billing import listeners as billing_listeners
        from books.billing.utils import init_billing_system
        bootstrap_system()
        init_billing_system()
        out_path = Path(settings.BASE_DIR).joinpath('tmp')
        out_path.mkdir(exist_ok=True) #Create tmp directory

        # Load fonts for ReportLab
        for font_name, font_path in getattr(settings, 'REGISTERED_FONTS',
            app_settings.REGISTERED_FONTS):
            pdfmetrics.registerFont( TTFont(font_name,
                Path(settings.BASE_DIR).joinpath(font_path))
            )

from appconf import AppConf

class BooksAppConf(AppConf):
    ACC_CHOICES = (
        ('A', 'Asset'),
        ('L', 'Liability'),
        ('C', 'Capital'),
        ('E', 'Expense'),
        ('R', 'Revenue'),
        ('P', 'Profits'),
        ('PU', 'Purchases'),
        ('LO', 'Losses'),
        ('CL', 'Customer'),
        ('S', 'Supplier')
        )

    CURRENCIES = (
        ('USD', 'USD'),
        )

    ACTIONS = (
        ('D', 'Debit'),
        ('C', 'Credit')
        )

    JOURNAL_PRESETS = (
        ('TB', 'Trial Balance'),
        ('BS', 'Balance Sheet'),
        ('CB', 'Cash Book'),
        ('PL', 'Trading, Profit & Loss'),
        ('T', 'Generic T-Account')
    )

    STANDARD_USER_GROUP_NAME = 'Standard Users'
    ADMIN_USER_GROUP_NAME = 'Admin Users'

    PDF_PAGE_WIDTH = 550

    PDF_STYLES = 'books.styles.style_options'
    DATE_FORMAT = '%d-%m-%Y'
    SHORT_DATE_FORMAT = '%d-%m'

    class Meta:
        prefix = 'opexa_books'

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
