import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from books.virtual.pdf import PDFBuilder
from books.conf.settings import ACTIONS

from .config import SystemAccount

class AccountGroup(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children')
    name = models.CharField(max_length = 100, primary_key = True)
    description = models.CharField(max_length = 300, blank = True, null = True)
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

    def __str__(self):
        if self.parent:
            return "{} - {}".format(str(self.parent).title(), str(self.name).title())
        else:
            return str(self.name).title()

    class Meta():
        ordering = ['name']

class Account(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name = 'parent account')
    code = models.CharField(max_length = 100,
        primary_key = True)
    name = models.CharField(max_length = 120,
        verbose_name = 'account name')
    account_group = models.ForeignKey('AccountGroup', models.CASCADE, blank = True)
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

    def save(self, *args, **kwargs):
        try:
            self.account_group
        except ObjectDoesNotExist:
            if self.parent:
                self.account_group = self.parent.account_group
        super().save(*args, **kwargs)
    
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

    def as_pdf(self, style,  as_at = None, include_descendants = False):
        table = self.as_t(as_at = as_at,
            include_descendants = include_descendants)
        builder = PDFBuilder()
        return builder.build(style, table)

    def all_entries(self, include_descendants = False):
        if include_descendants:
            all_accs = self._get_descendants(include_self  = True)
        else:
            all_accs = [self]
        return SingleEntry.objects.filter(account__in = all_accs)

    
    def balance(self, as_at = None):
        if as_at == None:
            as_at = timezone.now().date()

        all_accs = self._get_descendants(include_self  = True)

        debit_entries = SingleEntry.objects.filter(account__in = all_accs,
            action = 'D', date__lte = as_at)
        credit_entries = SingleEntry.objects.filter(account__in = all_accs,
            action = 'C', date__lte = as_at)
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

class SingleEntry(models.Model):
    account = models.ForeignKey('Account', models.CASCADE, blank = True)
    action = models.CharField(max_length = 1, choices = ACTIONS, blank = True)
    value = models.DecimalField(decimal_places = 2,
        max_digits = 15, null = True, blank = True)
    details = models.CharField(max_length = 300)
    date = models.DateField()
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

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
        verbose_name_plural = 'Single Entries'
        ordering = ['-date']

class TransactionDefinition(models.Model):
    description = models.CharField(max_length = 150)
    debit_account = models.ForeignKey('Account', on_delete = models.CASCADE,
        related_name = 'debit_transaction_definitions')
    credit_account = models.ForeignKey('Account', on_delete = models.CASCADE,
        related_name = 'credi_transaction_definitions')
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

class Transaction(models.Model):
    definition = models.ForeignKey('TransactionDefinition', null = True, blank = True,
        on_delete = models.CASCADE)
    debit_entry = models.ForeignKey('SingleEntry', on_delete = models.CASCADE,
        related_name = 'debit_transaction')
    credit_entry = models.ForeignKey('SingleEntry', on_delete = models.CASCADE,
        related_name = 'credit_transaction')
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

class DeclaredSource(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    account = models.ForeignKey('Account', on_delete = models.CASCADE)
    debit = models.DecimalField(max_digits = 15, decimal_places = 2,
        blank = True, null = True)
    credit = models.DecimalField(max_digits = 15, decimal_places = 2,
        blank = True, null = True)
    details = models.CharField(max_length = 140)
    date = models.DateField()
    system_account = models.ForeignKey(SystemAccount, models.CASCADE)

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
    