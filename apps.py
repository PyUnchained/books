from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django.conf import settings
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

    PDF_STYLES = 'books.styles.style_options'
    DATE_FORMAT = '%d-%m-%Y'
    SHORT_DATE_FORMAT = '%d-%m'

    LOGO_SMALL = None

    REGISTERED_FONTS = [
        ('Roboto', 'books/static/fonts/Roboto-Regular.ttf'),
        ('RobotoB', 'books/static/fonts/Roboto-Bold.ttf'),
        ('RobotoI', 'books/static/fonts/Roboto-Italic.ttf'),
        ('RobotoBI', 'books/static/fonts/Roboto-BoldItalic.ttf')
    ]

    class Meta:
        prefix = 'books'


class BooksConfig(AppConfig):
    name = 'books'
    verbose_name = 'OPEXA Accounting'

    def ready(self, *args, **kwargs):
        # Add listerners
        from books import listeners as books_listeners
        from books.billing import listeners as billing_listeners
        from books.billing.utils import init_billing_system

        try:
            bootstrap_system()
            init_billing_system()
        except:
            pass
        out_path = Path(settings.BASE_DIR).joinpath('tmp')
        out_path.mkdir(exist_ok=True) #Create tmp directory

        # Load fonts for ReportLab
        for font_name, font_path in settings.BOOKS_REGISTERED_FONTS:
            pdfmetrics.registerFont( TTFont(font_name,
                Path(settings.BASE_DIR).joinpath(font_path))
            )



def bootstrap_system():
    from django.contrib.auth.models import Group
    from books.models import Account
    from books.utils import create_default_account

    try:
        if Account.objects.all().count() <= 0:
            try:
                create_default_account()
            except :
                pass

    # Means the DB isn't ready yet
    except ProgrammingError:
        pass
