from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from books.models import JournalEntry, JournalEntryRule, JournalCreationRule
from books.forms import JournalEntryForm, JournalEntryRuleForm
from books.virtual.journal_entry_rules import initialize_form, build_journal
from books.virtual.forms import BaseRuleBasedTransactionForm

class BaseCreateView(CreateView):
    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data(**kwargs)
        return context

# Create your views here.
class NewJournalEntry(BaseCreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'interface.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return render(request, self.template_name, {'form': form, 'form_heading':
            'New Transaction'})

class NewJournalEntryRule(BaseCreateView):
    model = JournalEntryRule
    form_class = JournalEntryRuleForm
    template_name = 'interface.html'


class EnterTransactionView(View):
    form_class = BaseRuleBasedTransactionForm
    initial = {}
    template_name = 'interface.html'


    def get(self, request, *args, **kwargs):
        rule = JournalEntryRule.objects.get(pk = args[0])
        form = initialize_form(self.form_class, rule)
        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record {0}'.format(rule.name)})

    def post(self, request, *args, **kwargs):
        rule = JournalEntryRule.objects.get(pk = args[0])
        form = self.form_class(request.POST)
        form = initialize_form(self.form_class, rule, form = form)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record {0}'.format(rule.name)})

class JournalView(View):
    template_name = 'journal_interface.html'

    def get(self, request, *args, **kwargs):
        rule = JournalCreationRule.objects.get(pk = args[0])
        journal = build_journal(rule)
        return render(request, self.template_name, {'virtual_journal': journal})
