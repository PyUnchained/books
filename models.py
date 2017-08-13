import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.core.urlresolvers import reverse

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS, JOURNAL_PRESETS

INTEREST_METHODS = (
    ('S', 'Simple'),
    ('C', 'Compound')
)

def today():
    return timezone.now().date()


def year_ago(years = 1, from_date=timezone.now().date()):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

# Create your models here.
class OpexaBooksSystem(models.Model):
    system_code = models.CharField(primary_key = True, default=uuid.uuid4,
        max_length = 2000)

class AccountType(models.Model):
    name = models.CharField(max_length = 100, primary_key = True)
    description = models.CharField(max_length = 300, blank = True, null = True)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['name']

class AccountSubType(models.Model):
    name = models.CharField(max_length = 100, primary_key = True)
    description = models.CharField(max_length = 300, blank = True, null = True)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['name']

class Account(models.Model):
    code = models.CharField(max_length = 100,
        primary_key = True)
    name = models.CharField(max_length = 120)
    account_type = models.ForeignKey('AccountType', null = True)
    sub_type = models.ForeignKey('AccountSubType', null = True, blank = True)
    parent = models.ForeignKey('Account', blank = True, null = True,
        verbose_name = 'Grouped under',
        help_text = 'Describes the account under which this particular one is grouped.')

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
        debit_entries = SingleEntry.objects.filter(account = self,
            action = 'D').order_by('date')
        credit_entries = SingleEntry.objects.filter(account = self,
            action = 'C').order_by('date')

        debit = debit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        credit = credit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        return abs(debit - credit)

    def balance_as_at(self, from_date = None):
        if from_date == None:
            from_date = timezone.now().date()-timedelta(days = 365*10)

        debit_entries = SingleEntry.objects.filter(account = self,
            journal_entry__date__gte = from_date,
            action = 'D').order_by('date')
        credit_entries = SingleEntry.objects.filter(account = self,
            journal_entry__date__gte = from_date,
            action = 'C').order_by('date')

        debit = debit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        credit = credit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        return abs(debit - credit)


    def extra_data(self):
        pass
    
    def debit_minus_credit_balance(self, date__gte = None, date__lte = None):
        debit_entries = SingleEntry.objects.filter(account = self,
            journal_entry__date__gte = date__gte,
            journal_entry__date__lte = date__lte,
            action = 'D').order_by('date')
        credit_entries = SingleEntry.objects.filter(account = self,
            journal_entry__date__gte = date__gte,
            journal_entry__date__lte = date__lte,
            action = 'C').order_by('date')

        debit = debit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        credit = credit_entries.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        return debit - credit

    def balance_between(self, date__gte = None, date__lte = None):
        return abs(self.debit_minus_credit_balance(
            date__gte = date__gte, date__lte = date__lte))

    class Meta():
        ordering = ['name']

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
    rule = models.ForeignKey('JournalEntryRule', blank = True, null = True,
        help_text = 'Please select a rule, then save and continue.')
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

    @property
    def debit_entries(self):
        return SingleEntry.objects.filter(
                journal_entry = self, action = 'D')

    @property
    def credit_entries(self):
        return SingleEntry.objects.filter(
                journal_entry = self, action = 'C')

    @property
    def value(self):
        return SingleEntry.objects.filter(
                journal_entry = self,
                action = 'C').aggregate(
                    Sum('value'))['value__sum'] or Decimal('0.00')

class SingleEntry(models.Model):
    journal_entry = models.ForeignKey('JournalEntry')
    account = models.ForeignKey('Account')
    action = models.CharField(max_length = 1, choices = ACTIONS)
    value = models.DecimalField(decimal_places = 2,
        max_digits = 15, null = True)

    def __str__(self):
        if self.action == 'D':
            action = 'Debit'
        else:
            action = 'Credit'
        return "{0} {1}: {2}".format(action, self.account,
            self.value)

    class Meta():
        verbose_name_plural = 'Single Entries'
        ordering = ['-journal_entry__date']

class Branch(models.Model):
    name = models.CharField(max_length = 120)

    class Meta:
        verbose_name_plural = 'Branches'

class JournalEntryRule(models.Model):
    name = models.CharField(max_length = 200)
    term_sheet = models.ForeignKey('TermSheet', blank = True, null = True)
    allow_single_entry = models.BooleanField(default = False,
        help_text = 'If selected, system will no longer force debit '
        'and credit totals to match.')
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
    account_type = models.ManyToManyField('AccountType',
        blank = True,
        help_text = 'Choose one of account type or specific account.')
    sub_type = models.ManyToManyField('AccountSubType',
        blank = True)
    accounts = models.ManyToManyField('Account', verbose_name = 'Specific account',
        blank = True, help_text = 'Choose one of account type or specific account.')

class Journal(models.Model):
    code = models.CharField(max_length = 100,
        primary_key = True)
    name = models.CharField(max_length = 120)
    rule = models.ForeignKey('JournalCreationRule', blank = True, null = True,
        help_text = 'Custom user defined rule.')

    @property
    def link(self):
        return "<a href='{0}' class='btn-regular'>Download</a>".format(
            reverse('opexa_books:view_journal', args = (self.pk,)))

    def __str__(self):
        return self.name

class JournalCreationRule(models.Model):
    name = models.CharField(max_length = 120,
        null = True)
    preset = models.CharField(max_length = 2, choices = JOURNAL_PRESETS,
        null = True)
    date_from = models.DateField(default = year_ago)
    date_to = models.DateField(default = today)
    include_debt_from = models.ManyToManyField('Account',
        related_name = 'debt_included',
        help_text = 'Accounts from which to extract debt entries.',
        blank = True)
    reversed_debit_entries = models.ManyToManyField('Account',
        related_name = 'reversed_debit_entries',
        help_text = 'Reversed entries will appear on the credit side of the journal.',
        blank = True)
    include_credit_from = models.ManyToManyField('Account',
        related_name = 'credit_included',
        help_text = 'Accounts from which to extract credit entries.',
        blank = True)
    reversed_credit_entries = models.ManyToManyField('Account',
        related_name = 'reversed_credit_entries',
        help_text = 'Reversed entries will appear on the debit side of the journal.',
        blank = True)
    multi_column = models.BooleanField(default = False)
    latest_pdf = models.FileField(upload_to ='journal_pdfs', null = True, blank = True)
    default = models.BooleanField(default = False, editable = False)

    class Meta:
        verbose_name = 'Posting Rule'
        verbose_name_plural = 'Posting Rules'

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'None'

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

