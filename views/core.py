# import os

# from django.shortcuts import render
# from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# from django.views.generic.base import View
# from django.views.generic.detail import DetailView
# from django.views.generic.edit import CreateView, UpdateView
# from django.views.generic.list import ListView
# from django.conf import settings
# from django.forms.formsets import formset_factory
# from django.forms import modelformset_factory
# from django.template.loader import render_to_string
# from django.urls import reverse_lazy
# from django.db import transaction

# from books.models import JournalEntry, JournalEntryRule, JournalCreationRule, SingleEntry, Journal
# from books.forms import JournalEntryForm, JournalEntryRuleForm
# from books.virtual.journal_entry_rules import initialize_form, build_journal
# from books.virtual.forms import BaseRuleBasedTransactionForm
# from books.templatetags.forms import (DebitSingleEntryForm, CreditSingleEntryForm, SingleEntryFormSetHelper, SingleEntryForm, DebitEntryFormset, CreditEntryFormset,
#     GeneralDoubleEntryFormSetHelper, GeneralDoubleEntryFormSet, GeneralDoubleEntryBaseFormset)
# from books.virtual.journal import VirtualJournal

# def landing(request):

#     return render(request, 'books/landing.html')

# class DoubleEntryWidget(View):
#     form_class = BaseRuleBasedTransactionForm
#     initial = {}
#     template_name = 'books/double_entry_widget.html'
#     min_num = 2

#     def render_form_html_by_journal(journal_entry):
#         return render_to_string(self.template_name,
#             context = context, request = request)

#     def forsmet_initial_data(self, journal_entry):
#         initial = []
#         for i in range(self.min_num):
#             initial.append({'journal_entry':journal_entry})
#         return initial

#     def get(self, request, *args, **kwargs):
#         if args[0] == '':
#             journal_entry = JournalEntry()
#         else:
#             journal_entry = JournalEntry.objects.get(pk=args[0])

#         heading_message = "Double Entry"
#         formset = GeneralDoubleEntryFormSet(
#             initial = self.forsmet_initial_data(journal_entry)
#             )
#         formset_helper = GeneralDoubleEntryFormSetHelper()
#         formset_helper.form_action = reverse_lazy('open_books:admin_single_entries', args=(journal_entry.pk,))
#         form_html = render_to_string(self.template_name,
#             context = {'formset': formset,
#                 'heading': heading_message,
#                 'formset_helper':formset_helper},
#             request = request)
#         return JsonResponse({'form_html':form_html})

#     def post(self, request, *args, **kwargs):
#         with transaction.atomic():
#             journal_entry, created = JournalEntry.objects.get_or_create(pk=args[0])
#             formset = GeneralDoubleEntryFormSet(request.POST, request.FILES)
#             if formset.is_valid():
#                 # do something with the formset.cleaned_data
#                 print ('OK\n'*3)
#             else:
#                 heading_message = "Double Entry"
#                 formset_helper = GeneralDoubleEntryFormSetHelper()
#                 formset_helper.form_action = reverse_lazy('open_books:admin_single_entries', args=(journal_entry.pk,))
#                 form_html = render_to_string(self.template_name,
#                     context = {'formset': formset,
#                         'heading': heading_message,
#                         'formset_helper':formset_helper,
#                         'non_form_errors':formset.non_form_errors()},
#                     request = request)
#                 return JsonResponse({'form_html':form_html, 'success':False})
#         # return render(request, 'manage_articles.html', {'formset': formset})
#         # debit_form_helper = SingleEntryFormSetHelper()
#         # credit_form_helper = SingleEntryFormSetHelper()

#         # number_of_forms = 5
#         # querysets = initialize_form(SingleEntryForm, journal_entry.rule, return_qs = True)
#         # debit_initial_data = []
#         # for i in range(number_of_forms):
#         #     debit_initial_data.append({'journal_entry':journal_entry,
#         #         'queryset':querysets['debit_acc']['queryset']})
        
#         # credit_formset = CreditEntryFormset(request.POST,
#         #     form_kwargs = {'journal_entry': journal_entry,
#         #         'acc_qs':querysets['credit_acc']['queryset'],
#         #         'action':'C'},
#         #     prefix='credit', queryset=journal_entry.credit_entries)
#         # if credit_formset.is_valid():
#         #     debit_formset = DebitEntryFormset(request.POST,
#         #         form_kwargs={'journal_entry': journal_entry,
#         #         'acc_qs':querysets['debit_acc']['queryset'],
#         #         'action':'D'},
#         #         prefix='debit', queryset=journal_entry.debit_entries,
#         #         credit_formset = credit_formset)
#         #     if debit_formset.is_valid():
#         #         credit_formset.save()
#         #         debit_formset.save()
#         #         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


            

#         # else:
#         #     debit_formset = DebitEntryFormset(request.POST,
#         #         form_kwargs={'journal_entry': journal_entry,
#         #         'acc_qs':querysets['debit_acc']['queryset'],
#         #         'action':'D'},
#         #         prefix='debit', queryset=journal_entry.debit_entries)



#         # form_html = render_to_string('books/input_single_entries_popup.html',
#         #     context = {'debit_formset':debit_formset,
#         #         'debit_form_helper':debit_form_helper,
#         #         'credit_formset':credit_formset,
#         #         'journal_entry':journal_entry,
#         #         'credit_form_helper':credit_form_helper},
#         #     request = request)
#         # return JsonResponse({'form_html':form_html, 'success':False})

# class BaseCreateView(CreateView):
#     def get_context_data(self, **kwargs):
#         context = super(BaseCreateView, self).get_context_data(**kwargs)
#         return context

# # Create your views here.
# class NewJournalEntry(BaseCreateView):
#     model = JournalEntry
#     form_class = JournalEntryForm
#     template_name = 'interface.html'

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#         return render(request, self.template_name, {'form': form, 'form_heading':
#             'New Transaction'})

# class NewJournalEntryRule(BaseCreateView):
#     model = JournalEntryRule
#     form_class = JournalEntryRuleForm
#     template_name = 'interface.html'


# class EnterTransactionView(View):
#     form_class = BaseRuleBasedTransactionForm
#     initial = {}
#     template_name = 'enter_transaction_interface.html'


#     def get(self, request, *args, **kwargs):
#         rule = JournalEntryRule.objects.get(pk = args[0])
#         all_entries = JournalEntryRule.objects.all()
#         form = initialize_form(self.form_class, rule)
#         return render(request, self.template_name, {'form': form, 'form_heading':
#             'Record {0}'.format(rule.name), 'all_entries':all_entries})

#     def post(self, request, *args, **kwargs):
#         rule = JournalEntryRule.objects.get(pk = args[0])
#         form = self.form_class(request.POST)
#         all_entries = JournalEntryRule.objects.all()
#         form = initialize_form(self.form_class, rule, form = form)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#         return render(request, self.template_name, {'form': form, 'form_heading':
#             'Record {0}'.format(rule.name), 'all_entries':all_entries})

# class EnterAnyTransactionView(View):
#     form_class = BaseRuleBasedTransactionForm
#     initial = {}
#     template_name = 'enter_transaction_interface.html'


#     def get(self, request, *args, **kwargs):
#         rule = None
#         all_entries = JournalEntryRule.objects.all()
#         form = initialize_form(self.form_class, rule)
#         return render(request, self.template_name, {'form': form, 'form_heading':
#             'Record General Transaction', 'all_entries':all_entries})

#     def post(self, request, *args, **kwargs):
#         rule = None
#         all_entries = JournalEntryRule.objects.all()
#         form = self.form_class(request.POST)
#         form = initialize_form(self.form_class, rule, form = form)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#         return render(request, self.template_name, {'form': form, 'form_heading':
#             'Record General Transaction', 'all_entries':all_entries})

# class JournalListView(ListView):

#     model = JournalCreationRule
#     template_name = 'journal_list_view_interface.html'

#     def get_context_data(self, **kwargs):
#         context = super(JournalListView, self).get_context_data(**kwargs)
#         context['heading'] = 'Journals Available'
#         return context

#     # def get(self, request, *args, **kwargs):
#     #     rule = None
#     #     all_entries = JournalEntryRule.objects.all()
#     #     form = initialize_form(self.form_class, rule)
#     #     return render(request, self.template_name, {'form': form, 'form_heading':
#     #         'Record General Transaction', 'all_entries':all_entries})

# class JournalView(View):
#     """ Creates a Virtual Journal object using real-time data and redirects to a download
#     link for the pdf verion of it."""
#     template_name = 'journal_interface.html'

#     def get(self, request, *args, **kwargs):
#         journal = Journal.objects.get(code = args[0])
#         # if journal.rule.preset:
#         #     rule, created = JournalCreationRule.objects.get_or_create(
#         #         preset = journal.preset, default = True, before_date = journal.date_to,
#         #         after_date = journal.date_from, name =journal.name)
#         # else:
#         rule = journal.rule

#         virtual_journal = VirtualJournal(rule)
#         print (virtual_journal.pdf)
#         # file_path = virtual_journal.rule.latest_pdf.path
#         # if os.path.exists(file_path):
#         #     with open(file_path, 'rb') as fh:
#         response = HttpResponse(virtual_journal.pdf, content_type="application/pdf")
#         response['Content-Disposition'] = 'inline; filename=' + virtual_journal.pdf_name
#         return response
#         # return render(request, self.template_name, {'virtual_journal': journal})
