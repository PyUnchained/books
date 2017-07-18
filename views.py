import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.conf import settings
from django.forms.formsets import formset_factory
from django.template.loader import render_to_string

from books.models import JournalEntry, JournalEntryRule, JournalCreationRule
from books.forms import JournalEntryForm, JournalEntryRuleForm
from books.virtual.journal_entry_rules import initialize_form, build_journal
from books.virtual.forms import BaseRuleBasedTransactionForm
from books.templatetags.forms import DebitSingleEntryForm, CreditSingleEntryForm, SingleEntryFormSetHelper, SingleEntryForm

def landing(request):

    return render(request, 'books/landing.html')

class AdminSingleEntryView(View):
    form_class = BaseRuleBasedTransactionForm
    initial = {}
    template_name = 'books/admin_popup.html'

    def post(self, request, *args, **kwargs):
        journal_entry = JournalEntry.objects.get(pk=args[0])
        debit_form_helper = SingleEntryFormSetHelper()
        DebitEntryFormset = formset_factory(DebitSingleEntryForm)
        CreditEntryFormset = formset_factory(CreditSingleEntryForm,
            min_num=1, validate_min=True)

        number_of_forms = 4
        querysets = initialize_form(SingleEntryForm, journal_entry.rule, return_qs = True)
        debit_initial_data = []
        for i in range(number_of_forms):
            debit_initial_data.append({'journal_entry':journal_entry,
                'queryset':querysets['debit_acc']['queryset']})

        credit_data = []
        for i in range(number_of_forms):
            credit_data.append({'journal_entry':journal_entry,
                'queryset':querysets['credit_acc']['queryset']})

        debit_formset = DebitEntryFormset(request.POST,
            initial = debit_initial_data)
        credit_formset = CreditEntryFormset(request.POST,
            initial = credit_data)

        if debit_formset.is_valid() and credit_formset.is_valid():
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        for f in debit_formset.forms:
            print(f)


        form_html = render_to_string('books/admin_popup.html',
            context = {'debit_formset':debit_formset,
                'debit_form_helper':debit_form_helper,
                'credit_formset':credit_formset,
                'journal_entry':journal_entry},
            request = request)
        return JsonResponse({'form_html':form_html})

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
    template_name = 'enter_transaction_interface.html'


    def get(self, request, *args, **kwargs):
        rule = JournalEntryRule.objects.get(pk = args[0])
        all_entries = JournalEntryRule.objects.all()
        form = initialize_form(self.form_class, rule)
        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record {0}'.format(rule.name), 'all_entries':all_entries})

    def post(self, request, *args, **kwargs):
        rule = JournalEntryRule.objects.get(pk = args[0])
        form = self.form_class(request.POST)
        all_entries = JournalEntryRule.objects.all()
        form = initialize_form(self.form_class, rule, form = form)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record {0}'.format(rule.name), 'all_entries':all_entries})

class EnterAnyTransactionView(View):
    form_class = BaseRuleBasedTransactionForm
    initial = {}
    template_name = 'enter_transaction_interface.html'


    def get(self, request, *args, **kwargs):
        rule = None
        all_entries = JournalEntryRule.objects.all()
        form = initialize_form(self.form_class, rule)
        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record General Transaction', 'all_entries':all_entries})

    def post(self, request, *args, **kwargs):
        rule = None
        all_entries = JournalEntryRule.objects.all()
        form = self.form_class(request.POST)
        form = initialize_form(self.form_class, rule, form = form)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return render(request, self.template_name, {'form': form, 'form_heading':
            'Record General Transaction', 'all_entries':all_entries})

class JournalListView(ListView):

    model = JournalCreationRule
    template_name = 'journal_list_view_interface.html'

    def get_context_data(self, **kwargs):
        context = super(JournalListView, self).get_context_data(**kwargs)
        context['heading'] = 'Journals Available'
        return context

    # def get(self, request, *args, **kwargs):
    #     rule = None
    #     all_entries = JournalEntryRule.objects.all()
    #     form = initialize_form(self.form_class, rule)
    #     return render(request, self.template_name, {'form': form, 'form_heading':
    #         'Record General Transaction', 'all_entries':all_entries})

class JournalView(View):
    template_name = 'journal_interface.html'

    def get(self, request, *args, **kwargs):
        rule = JournalCreationRule.objects.get(pk = args[0])
        journal = build_journal(rule)
        file_path = journal.rule.latest_pdf.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + journal.rule.latest_pdf.path
                return response
        # return render(request, self.template_name, {'virtual_journal': journal})
