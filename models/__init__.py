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

    STANDARD_USER_GROUP_NAME = 'Standard Users'
    ADMIN_USER_GROUP_NAME = 'Admin Users'

    PDF_PAGE_WIDTH = 550

    PDF_STYLES = 'books.styles.style_options'
    DATE_FORMAT = '%d-%m-%Y'
    SHORT_DATE_FORMAT = '%d-%m'

    class Meta:
        prefix = 'opexa_books'
        
from .accounts import *
from .config import *
from .auth import *
from .billing import *