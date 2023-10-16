from django import forms

from .core import RequestUserSystemAccountAdminFormMixin
from books.models import (Account, AccountGroup, SingleEntry, Transaction, TransactionDefinition,
    SystemAccount)

class SingleEntryAdminForm(forms.ModelForm):

    class Meta:
        model = SingleEntry
        exclude = []


class AccountAdminForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'code', 'parent', 'account_group', 'system_account']

class TransactionDefinitionAdminForm(forms.ModelForm):

    class Meta:
        model = TransactionDefinition
        exclude = []

class TransactionAdminForm(forms.ModelForm):

    class Meta:
        model = Transaction
        exclude = []