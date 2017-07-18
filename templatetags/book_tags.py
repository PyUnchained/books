from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import formset_factory
from django.contrib.contenttypes.models import ContentType
from django.forms.formsets import formset_factory

from books.models import JournalEntry
from books.virtual.journal_entry_rules import initialize_form
from books.templatetags.forms import (SingleEntryForm, SingleEntryFormSetHelper,
    DebitSingleEntryForm, CreditSingleEntryForm)

register = template.Library()

@register.inclusion_tag('account_history_table.html')
def account_history(account):

    debit_entries = JournalEntry.objects.filter(debit_acc = account).order_by('date')
    credit_entries = JournalEntry.objects.filter(credit_acc = account).order_by('date')
    return {'debit_entries':debit_entries, 'credit_entries':credit_entries}

@register.inclusion_tag('books/popup_base.html')
def pop_up(instance = None):
    print (instance)
    content = 'Pies'
    return {'content':content}

@register.inclusion_tag('books/admin_popup.html')
def admin_popup(obj, model = 'JournalEntry'):
    if model == 'JournalEntry':
        number_of_forms = 4
        querysets = initialize_form(SingleEntryForm, obj.rule, return_qs = True)
        debit_initial_data = []
        for i in range(number_of_forms):
            debit_initial_data.append({'journal_entry':obj,
                'queryset':querysets['debit_acc']['queryset']})
        DebitEntryFormset = formset_factory(DebitSingleEntryForm)
        debit_formset = DebitEntryFormset(initial = debit_initial_data)

        credit_data = []
        for i in range(number_of_forms):
            credit_data.append({'journal_entry':obj,
                'queryset':querysets['credit_acc']['queryset']})
        DebitEntryFormset = formset_factory(CreditSingleEntryForm)
        credit_formset = DebitEntryFormset(initial = credit_data)

        debit_form_helper = SingleEntryFormSetHelper()
    return {'debit_formset':debit_formset, 'debit_form_helper':debit_form_helper,
        'credit_formset':credit_formset, 'journal_entry':obj}