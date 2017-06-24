from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import formset_factory
from django.contrib.contenttypes.models import ContentType

from books.models import JournalEntry

register = template.Library()

@register.inclusion_tag('account_history_table.html')
def account_history(account):

    debit_entries = JournalEntry.objects.filter(debit_acc = account).order_by('date')
    credit_entries = JournalEntry.objects.filter(credit_acc = account).order_by('date')
    return {'debit_entries':debit_entries, 'credit_entries':credit_entries}