import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS, JOURNAL_PRESETS

INTEREST_METHODS = (
    ('S', 'Simple'),
    ('C', 'Compound')
)

# Create your models here.
class OpexaBooksSystem(models.Model):
    system_code = models.CharField(primary_key = True, default=uuid.uuid4,
        max_length = 2000)

class AccountType(models.Model):
    name = models.CharField(max_length = 100, primary_key = True)
    description = models.CharField(max_length = 300, blank = True, null = True)

    def __str__(self):
        return self.name

class Account(models.Model):
    code = models.CharField(max_length = 100,
        primary_key = True)
    name = models.CharField(max_length = 120)
    account_type = models.ForeignKey('AccountType', null = True)
    parent = models.ForeignKey('Account', blank = True, null = True,
        verbose_name = 'Group Account Under')

    def __str__(self):
        if self.parent:
            names = []
            for p in self.parents:
                names.append(p.name)
            names.append(self.name)
            return ' - '.join(names)
        return self.name

    @property
    def parents(self):
        parents = []
        current = self
        while True:
            if current.parent:
                parents.append(current.parent)
                current = current.parent
            else:
                return parents

            

    @property
    def balance(self):
        debit_entries = JournalEntry.objects.filter(debit_acc = self).order_by('date')
        credit_entries = JournalEntry.objects.filter(credit_acc = self).order_by('date')

        debit = Decimal(0)
        credit = Decimal(0)
        for e in debit_entries:
            debit += e.value
        for e in credit_entries:
            credit += e.value
        return abs(debit - credit)

    def extra_data(self):
        pass
    
    def debit_minus_credit_balance(self, date__gte = None, date__lte = None):
        debit_entries = JournalEntry.objects.filter(debit_acc = self,
            date__gte = date__gte, date__lte = date__lte).order_by('date')
        credit_entries = JournalEntry.objects.filter(credit_acc = self,
            date__gte = date__gte, date__lte = date__lte).order_by('date')

        debit = Decimal(0)
        credit = Decimal(0)
        for e in debit_entries:
            debit += e.value
        for e in credit_entries:
            credit += e.value
        return debit - credit

class JournalEntry(models.Model):
    code = models.UUIDField(max_length = 100,
        primary_key = True, default=uuid.uuid4)
    debit_acc = models.ManyToManyField('Account',
        related_name = 'debit_entry',
        verbose_name = 'debit')
    credit_acc = models.ManyToManyField('Account',
        related_name = 'credit_entry',
        verbose_name = 'credit')
    debit_branch = models.ForeignKey('Branch',
        related_name = 'debit_branch', null = True,verbose_name = 'branch',
        blank = True)
    credit_branch = models.ForeignKey('Branch',
        related_name = 'credit_branch', null = True,verbose_name = 'branch',
        blank = True)
    term = models.FloatField(null = True, help_text = 'In Days')
    date = models.DateField(null = True)
    currency = models.CharField(choices = CURRENCIES, max_length = 3,
        default = 'USD', null = True)
    value = models.DecimalField(decimal_places = 2,
        max_digits = 15, null = True)
    rule = models.ForeignKey('JournalEntryRule', blank = True, null = True)
    details = models.TextField(max_length = 2000, blank = True, null = True)
    approved = models.BooleanField(default = False)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        if self.rule:
            return self.rule.name
        elif self.details:
            return self.details
        else:
            return str(self.code)

class SingleEntry(models.Model):
    journal_entry = models.ForeignKey('JournalEntry')
    account = models.ForeignKey('Account', blank = True)
    value = models.DecimalField(decimal_places = 2,
        max_digits = 15, null = True, blank = True)

class Branch(models.Model):
    name = models.CharField(max_length = 120)

    class Meta:
        verbose_name_plural = 'Branches'

class JournalEntryRule(models.Model):
    name = models.CharField(max_length = 200)
    term_sheet = models.ForeignKey('TermSheet', blank = True, null = True)
    display_template = models.TextField(max_length = 2000,
        blank = True, null = True)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        verbose_name = 'Transaction Definition'
        verbose_name_plural = 'Transaction Definitions'


class JournalEntryAction(models.Model):
    rule = models.ForeignKey('JournalEntryRule')
    action = models.CharField(choices = ACTIONS, max_length = 1)
    account_type = models.ForeignKey('AccountType', null = True,
        blank = True,
        help_text = 'Choose one of account type or specific account.')
    account = models.ForeignKey('Account', verbose_name = 'Specific account',
        blank = True, null = True,
        help_text = 'Choose one of account type or specific account.')

class Journal(models.Model):
    code = models.CharField(max_length = 100,
        primary_key = True)
    name = models.CharField(max_length = 120)

class JournalCreationRule(models.Model):
    name = models.CharField(max_length = 120,
        null = True)
    preset = models.CharField(max_length = 2, choices = JOURNAL_PRESETS, blank = True,
        null = True)
    after_date = models.DateField(null = True)
    before_date = models.DateField(default = timezone.now)
    include_debt_from = models.ManyToManyField('Account',
        related_name = 'debt_included',
        help_text = 'Accounts from which to extract debt entries.')
    reversed_debit_entries = models.ManyToManyField('Account',
        related_name = 'reversed_debit_entries',
        help_text = 'Reversed entries will appear on the credit side of the journal.',
        blank = True)
    include_credit_from = models.ManyToManyField('Account',
        related_name = 'credit_included',
        help_text = 'Accounts from which to extract credit entries.')
    reversed_credit_entries = models.ManyToManyField('Account',
        related_name = 'reversed_credit_entries',
        help_text = 'Reversed entries will appear on the debit side of the journal.',
        blank = True)
    multi_column = models.BooleanField(default = False)
    latest_pdf = models.FileField(upload_to ='journal_pdfs', null = True, blank = True)

    class Meta:
        verbose_name = 'Posting Rule'
        verbose_name_plural = 'Posting Rules'

    def __str__(self):
        return self.name

class Upload(models.Model):
    description = models.CharField(max_length = 200)
    file = models.FileField(upload_to = 'upload_docs')

class Settlement(models.Model):
    account = models.ForeignKey('Account')
    initial_amount = models.DecimalField(max_digits = 15, decimal_places = 2)
    term = models.IntegerField(default = 90)
    term_sheet = models.ForeignKey('TermSheet')

class TermSheet(models.Model):
    """
    Defines how a particular investment shoud appreciate/depreciate over time.
    """
    description = models.CharField(max_length = 120)
    interest_method = models.CharField(max_length = 2, choices = INTEREST_METHODS,
        default = 'S')
    last_modified = models.DateTimeField(auto_now = True,
        null = True, editable = False)
    date_issued = models.DateField(null = True, blank = True)
    expiry_date = models.DateField(null = True, blank = True)
    security = models.ForeignKey('Upload', related_name = 'ts_security',
        null = True, blank = True)
    guarantee = models.ForeignKey('Upload', related_name = 'ts_guarantee',
        null = True, blank = True)
    recourse_measures = models.ManyToManyField('Upload', blank = True,
        related_name = 'ts_recourse')
    buffer_days = models.IntegerField('Buffer', default = 7)
    max_value = models.DecimalField('Max Value ($)', max_digits = 15, decimal_places = 2)
    min_value = models.DecimalField('Min Value ($)', max_digits = 15, decimal_places = 2)

    establishment_fee_rate = models.DecimalField('Establishment Fee (%)',
        max_digits = 7, decimal_places = 4)
    roll_over_fee_rate = models.DecimalField(
        'Rollover Fee (%)',
        max_digits = 7, decimal_places = 4,
        null = True, blank = True)           
    default_fee_rate = models.DecimalField(
        'Default Fee (%)',
        max_digits = 7, decimal_places = 4,
        null = True, blank = True)

    discount_rate = models.DecimalField('Monthly Discount Rate (%)', max_digits = 5, decimal_places = 2)
    rollover_discount_rate = models.DecimalField('Monthly Rollover Discount Rate (%)', max_digits = 5, decimal_places = 2,
        null = True, blank = True)
    default_discount_rate = models.DecimalField('Monthly Default Discount Rate (%)', max_digits = 5, decimal_places = 2,
        null = True, blank = True)

    pdf_version = models.FileField(upload_to = 'pdf_termsheets/', blank = True,
        null = True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Term Sheet'
        verbose_name_plural = 'Term Sheets'

    def decimal_discount_rates(self, period = 'monthly'):
        rates = ['discount_rate', 'rollover_discount_rate', 'default_discount_rate']
        resp = []
        if period == 'monthly':
            for r in rates:
                val = getattr(self, r)
                if val:
                    resp.append(val/Decimal(30.00)/Decimal(100))
                else:
                    resp.append(Decimal(0))
        return resp

    def decimal_fee_rates(self, period = 'monthly'):
        rates = ['establishment_fee_rate', 'roll_over_fee_rate', 'default_fee_rate']
        resp = []
        if period == 'monthly':
            for r in rates:
                val = getattr(self, r)
                if val:
                    resp.append(val/Decimal(100))
                else:
                    resp.append(Decimal(0))
        return resp

