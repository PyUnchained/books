from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.forms import formset_factory
from django.contrib.contenttypes.models import ContentType
from django.forms.formsets import formset_factory

from books.models import JournalEntry, SingleEntry
from books.virtual.journal_entry_rules import initialize_form
from books.templatetags.forms import (SingleEntryForm, SingleEntryFormSetHelper,
    DebitSingleEntryForm, CreditSingleEntryForm)

register = template.Library()

@register.inclusion_tag('account_history_table.html')
def account_history(account):

    debit_entries = SingleEntry.objects.filter(account = account,
        action = 'D').order_by('journal_entry__date')
    credit_entries = SingleEntry.objects.filter(account = account,
        action = 'C').order_by('journal_entry__date')
    return {'debit_entries':debit_entries, 'credit_entries':credit_entries}

@register.inclusion_tag('books/popup_base.html')
def pop_up(instance = None):
    print (instance)
    content = 'Pies'
    return {'content':content}

@register.inclusion_tag('books/popup_base.html')
def admin_base_popup(form_url = None):
    return {}