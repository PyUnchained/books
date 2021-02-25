from decimal import Decimal

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.forms import formset_factory


from books.models import Account, AccountGroup, DeclaredSource, SingleEntry
from books.forms import NewSourceForm, SourceDeclarationForm, InitializeIntegratedAccountForm
from books.utils import register_new_account, chart_of_accounts_setup

class InitializeIntegratedAccountView(View):
    template_name = 'books/dashboard/initialize_integrated_acc.html'
    def get(self, request, *args, **kwargs):
        form = InitializeIntegratedAccountForm()
        ctx = {'username':request.user.username,'form':form}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        ctx = {}
        with transaction.atomic():
            acc = register_new_account(user = request.user,
                name = request.user.username)

        messages.add_message(request, messages.SUCCESS, "Accounts initialized.")
        return HttpResponseRedirect(reverse_lazy('admin:index'))





class DeclareSourcesView(View):

    form_class = None
    root_account_group = ''
    prev_url = ''
    this_url = ''
    next_url = ''
    end_url = ''
    template_name = 'books/declare_sources.html'

    def _existing_delarations(self, system_account):
        table = []
        debit_total = Decimal('0.00')
        credit_total = Decimal('0.00')
        for source in  DeclaredSource.objects.filter(
            system_account = system_account).order_by('date'):

            row_cells = [source.date, "{} ({})".format(source.account.short_name,source.account.account_group.short_name),
                source.details]
            if source.debit:
                debit_total += source.debit
                value_cells = [source.debit, '-']
            else:
                credit_total += source.credit
                value_cells = ['-', source.credit]
            row_cells.extend(value_cells)
            table.append(row_cells)
        table.append(['', '', '', debit_total, credit_total])
        return table

    def get(self, request, *args, **kwargs):
        new_source_form = NewSourceForm(self.root_account_group,
            request.user.account)
        source_declaration_form = SourceDeclarationForm(self.root_account_group,
            request.user.account)
        existing_declarations = self._existing_delarations(request.user.account)
        if self.next_url:
            next_url = reverse_lazy(self.next_url)
        else:
            next_url = None

        if self.prev_url:
            prev_url = reverse_lazy(self.prev_url)
        else:
            prev_url = None

        if self.end_url:
            end_url = reverse_lazy(self.end_url)
        else:
            end_url = None

        ctx = {'new_source_form':new_source_form,
            'root_account_group':self.root_account_group,
            'source_declaration_form':source_declaration_form,
            'existing_declarations':existing_declarations,
            'next_url': next_url, 'prev_url':prev_url,
            'end_url':end_url, 'show_new_source_form':False}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        #Setup both forms in their default state
        ctx = {'show_new_source_form':False}
        new_source_form = NewSourceForm(self.root_account_group,
            request.user.account)
        source_declaration_form = SourceDeclarationForm(self.root_account_group,
            request.user.account)
        existing_declarations = self._existing_delarations(request.user.account)
        if self.next_url:
            next_url = reverse_lazy(self.next_url)
        else:
            next_url = None

        if self.prev_url:
            prev_url = reverse_lazy(self.prev_url)
        else:
            prev_url = None

        if self.end_url:
            end_url = reverse_lazy(self.end_url)
        else:
            end_url = None

        #Determine what to do based on which submit button on the page was clicked
        if 'new_declaration' in request.POST:
            source_declaration_form = SourceDeclarationForm(self.root_account_group,
                request.user.account, request.POST)

            if source_declaration_form.is_valid():
                declaration = source_declaration_form.save(commit = False)
                declaration.system_account = request.user.account
                declaration.save()
                messages.add_message(request, messages.SUCCESS, "Success")
                return HttpResponseRedirect(reverse_lazy(self.this_url))

        if 'new_source' in request.POST:
            new_source_form = NewSourceForm(self.root_account_group,
                request.user.account, request.POST)

            if new_source_form.is_valid():
                source = new_source_form.save(commit = False)
        
                if source.parent:
                    source.account_group = source.parent.account_group

                source.system_account = request.user.account
                source.save()
                messages.add_message(request, messages.SUCCESS, "Success")
                return HttpResponseRedirect(reverse_lazy(self.this_url))

            ctx.update({'show_new_source_form':True})


        

        ctx.update({'new_source_form':new_source_form,
            'root_account_group':self.root_account_group,
            'source_declaration_form':source_declaration_form,
            'existing_declarations':existing_declarations,
            'next_url': next_url, 'prev_url':prev_url,
            'end_url':end_url})
        return render(request, self.template_name, ctx)


class CapitalSourcesView(DeclareSourcesView):

    form_class = None
    root_account_group = 'equity'
    this_url = 'opexa_books:capital_sources'
    next_url = 'opexa_books:liability_sources'

class LiabilitySourcesView(DeclareSourcesView):

    form_class = None
    root_account_group = 'liability'
    prev_url = 'opexa_books:capital_sources'
    this_url = 'opexa_books:liability_sources'
    next_url = 'opexa_books:asset_sources'

class AssetsSourcesView(DeclareSourcesView):

    form_class = None
    root_account_group = 'assets'
    prev_url = 'opexa_books:liability_sources'
    this_url = 'opexa_books:asset_sources'
    end_url = 'opexa_books:end_declarations'

def end_declarations_view(request):
    system_account = request.user.account
    declarations = DeclaredSource.objects.filter(system_account = system_account)
    with transaction.atomic():
        for d in declarations:
            if d.is_debit:
                action = 'D'
            else:
                action = 'C'
            s_entry_dict = {'account':d.account, 'action':action,
            'value':d.value, 'details':d.details, 'date':d.date,
            'system_account':system_account}
            SingleEntry.objects.create(**s_entry_dict)
            d.delete()

        request.user.account.initial_setup_done = True

    messages.add_message(request, messages.SUCCESS, "Opening Financial Position Declared")
    return HttpResponseRedirect(reverse_lazy('opexa_books:dashboard'))

