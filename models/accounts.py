import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import transaction
from django.contrib.contenttypes.models import ContentType



from mptt.models import MPTTModel, TreeForeignKey

from books.virtual.pdf import TAccountPDFBuilder
from books.blockchain import BlockchainMixin



INCREASE_BALANCE_OPTIONS = (
    ('', 'None'),
    ('D', 'Debit'),
    ('C', 'Credit'),
    )

class SingleEntryCreatorMixin():

    @property
    def single_entry_ref_code(self):
        ct = ContentType.objects.get_for_model(self)
        return '{}-{}-{}'.format(ct.app_label, ct.model, self.pk)


class AccountGroup(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name = 'parent account group')
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 300, blank = True, null = True)
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)

    @property
    def short_name(self):
        return self.name.title()

    @property
    def root_name(self):
        return self.get_root().name.title()

    def __str__(self):
        if self.parent:
            return "{} - {}".format(str(self.parent).title(), str(self.name).title())
        else:
            return str(self.name).title()

    class Meta():
        ordering = ['name']
        unique_together = ['name', 'system_account']

class Account(MPTTModel, BlockchainMixin):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name = 'parent account')
    code = models.CharField(max_length = 100, blank = True, null = True)
    name = models.CharField(max_length = 120, verbose_name = 'account name')
    account_group = models.ForeignKey('AccountGroup', models.CASCADE, blank = True, null = True)
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE, blank = True, null = True)
    increase_balance = models.CharField(max_length =1, choices = INCREASE_BALANCE_OPTIONS, default = '')
    address_id = models.CharField(max_length = 120, blank = True, null = True)
    adeler_groups = {
        'ADE':['current_assets', 'cost_of_sales', 'expense', 'long-term assets'],
        'LER':['current_liabilities', 'equity','income', 'long-term liabilities']
    }

    @property
    def short_name(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if self.parent:
            self.account_group = self.parent.account_group

        if self.increase_balance == '' and self.account_group:
            self.increase_balance = self._guess_increase_method()

        if not self.system_account:
            self.system_account = "books.SystemAccount".objects.get(name = "opexa_books")

        super().save(*args, **kwargs)

    def _guess_increase_method(self):
        """
        When not explicitly stated, guesses whether the balance of the account should
        increase/decrease when a debit entry is recorded based on the account group.
        """

        increase_on_debit = ['current assets', 'long-term assets', 'cost of sales', 'expense']
        root_account_groups = AccountGroup.objects.filter(name__in = increase_on_debit)
        debit_increase_groups = AccountGroup.objects.get_queryset_descendants(root_account_groups,
            include_self = True)

        if self.account_group in debit_increase_groups:
            return 'D'
        else:
            return 'C'
    
    def __str__(self):
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

    def _get_descendants(self, **kwargs):
        try:
            return self.get_descendants(**kwargs)
        except ValueError:
            return [self]

    def as_dict(self, as_at = None, include_descendants = False):
        if as_at == None:
            as_at = timezone.now().date()

        table = {'heading':str(self), 'as_at':as_at, 'debit':[],
            'credit':[]}
        entries = self.all_entries(include_descendants = include_descendants)
        for e in entries:
            if e.action == 'D':
                table['debit'].append(e)
            else:
                table['credit'].append(e)
        return table

    def as_t(self, as_at = None, include_descendants = False):
        table_dict = self.as_dict(as_at = as_at,
            include_descendants = include_descendants)
        table = []
        table.append([table_dict['heading']])

        table.append(['Date', 'Details', 'Amt']*2)
        max_entries_on_side = max([len(table_dict['credit']), len(table_dict['debit'])])

        sides = ['debit', 'credit']
        #Build the T-Account line by line, taking into account the fact that one side will likely
        #have more entries on one side than it does on the other side.
        debit_total = Decimal('0.00')
        credit_total = Decimal('0.00')
        for line_num in range(max_entries_on_side):
            printed_line = []

            #If there is no entry on both sides (i.e. we've already recorded all of the entries
            #present on either the credit or debit side) make sure the new entry just has a blank
            #line
            for s in sides:
                try:
                    entry = table_dict[s][line_num]
                    entry_as_list = [entry.date, entry.details, entry.value]
                    printed_line.extend(entry_as_list)
                except IndexError:
                    entry_as_list = ['', '', '']
                    printed_line.extend(entry_as_list)
            table.append(printed_line)

        return table

    def as_pdf(self,  as_at = None, include_descendants = False, file_name = None):
        table = self.as_t(as_at = as_at,
            include_descendants = include_descendants)
        builder = TAccountPDFBuilder()
        return builder.build(table, file_name = file_name)

    def all_entries(self, include_descendants = False):
        if include_descendants:
            all_accs = self._get_descendants(include_self  = True)
        else:
            all_accs = [self]
        return SingleEntry.objects.filter(account__in = all_accs)

    
    def balance(self, as_at = None, from_date = None, include_descendants = False, full = False):

        if as_at == None:
            as_at = timezone.now().date()
        
        if include_descendants:
            all_accs = self._get_descendants(include_self  = True)
        else:
            all_accs = [self]

        query_kwargs = {'account__in' : all_accs, 'date__lte' : as_at}
        if from_date:
            query_kwargs.update({'date__gte':from_date})



        single_entries = SingleEntry.objects.filter(**query_kwargs)
        total = Decimal('0.00')
        for entry in single_entries:
            if entry.action == self.increase_balance:

                total += entry.value
            else:
                total -= entry.value
        if full:
            return (self.increase_balance, total)
        else:
            return total


    def positive_action(self):
        pass


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
        unique_together = ('system_account', 'code')

class SingleEntry(models.Model, BlockchainMixin):
    account = models.ForeignKey('Account', models.CASCADE)
    action = models.CharField(max_length = 1, choices = settings.BOOKS_ACTIONS)
    value = models.DecimalField(decimal_places = 2,
        max_digits = 15, null = True)
    details = models.CharField(max_length = 300)
    date = models.DateField()
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)
    double_entry = models.ForeignKey('DoubleEntry', models.CASCADE,
        null = True, blank = True, editable = False)
    creator_ref = models.CharField(max_length = 200, blank = True, null = True,
        editable = False) 

    def __str__(self):
        if self.action == 'D':
            action = 'Debit'
        else:
            action = 'Credit'

        #Catch exception that occurs when there's no account associated with the single
        #entry
        try :
            return "{0} {1}: {2}".format(action, self.account,
                self.value)
        except Account.DoesNotExist:
            return "{0} {1}: {2}".format(action, 'N/A',
                self.value)

    class Meta():
        verbose_name_plural = 'Single entries'
        ordering = ['-date']

class DoubleEntry(models.Model):
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)
    date = models.DateField()
    details = models.CharField(max_length = 300)
    related_document = models.FileField(upload_to = 'double_entry_files',
        blank = True, null = True)
    creator_ref = models.CharField(max_length = 200, blank = True, null = True,
        editable = False) 
    
    class Meta():
        verbose_name_plural = 'Double entries'
        ordering = ['-date']

    @classmethod
    def record(cls, debits = [], credits = [], **record_kwargs):

        entry_dict = {'D':debits, 'C':credits}
        balance_sum = {'D':Decimal('0.00'), 'C':Decimal('0.00')}
        all_entries = []

        def inflate_single_entry_dict(entry_dict, **kwargs):
            entry_dict.update(kwargs)
            return entry_dict

        for action, entries in entry_dict.items():
            for e in entries:
                e = inflate_single_entry_dict(e, action = action, **record_kwargs)
                all_entries.append(e)
                balance_sum[action] += Decimal(e['value'])

        if balance_sum['D'] != balance_sum['C']:
            raise AccountingPrincipleError('''Invalid double entry: Debit and Credit values did not 
                match!''')

        with transaction.atomic():
            double_entry = cls.objects.create(**record_kwargs)
            for entry_dict in all_entries:
                SingleEntry.objects.create(double_entry = double_entry, **entry_dict)

        return double_entry


    def __str__(self):
        return f"{self.details} - {self.date}"
    

class TransactionDefinition(models.Model):
    description = models.CharField(max_length = 150)
    debit_account = models.ForeignKey('Account', on_delete = models.CASCADE,
        related_name = 'debit_transaction_definitions')
    credit_account = models.ForeignKey('Account', on_delete = models.CASCADE,
        related_name = 'credi_transaction_definitions')
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)
    short_code = models.CharField(max_length = 10, blank = True, null = True)

    def __str__(self):
        return self.description

class Transaction(models.Model):
    definition = models.ForeignKey('TransactionDefinition', null = True, blank = True,
        on_delete = models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(max_digits = 15, decimal_places = 2, null = True)
    details = models.TextField(max_length = 2000, blank = True, null = True)
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)
    double_entry_record = models.ForeignKey('DoubleEntry', models.SET_NULL,
        blank = True, null = True)

    def __str__(self):
        return f"{self.definition} - {self.date}"

    def commit(self):
        """ Generates the double entry record related to this transaction """
        debits = [{"account" :self.definition.debit_account, "value": self.value}]
        credits = [{"account" :self.definition.credit_account, "value": self.value}]
        self.double_entry_record = DoubleEntry.record(debits = debits, credits = credits, system_account = self.system_account,
            date = self.date, details = self.details)
        self.save()



class DeclaredSource(models.Model):
    system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)
    account = models.ForeignKey('Account', on_delete = models.CASCADE)
    debit = models.DecimalField(max_digits = 15, decimal_places = 2,
        blank = True, null = True)
    credit = models.DecimalField(max_digits = 15, decimal_places = 2,
        blank = True, null = True)
    details = models.CharField(max_length = 140)
    date = models.DateField()
    # system_account = models.ForeignKey("books.SystemAccount", models.CASCADE)

    @property
    def is_debit(self):
        if self.debit:
            return True
        return False

    @property
    def value(self):
        if self.debit:
            val = self.debit
        else:
            val = self.credit
        return val
    