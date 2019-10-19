from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages


from books.models import Account, AccountGroup
from books.forms import NewSourceForm, SourceDeclarationForm

class DeclareSourcesView(View):

    form_class = None
    root_account_group = ''
    this_url = ''
    template_name = 'books/declare_sources.html'

    def get(self, request, *args, **kwargs):
        new_source_form = NewSourceForm(self.root_account_group)
        source_declaration_form = SourceDeclarationForm(self.root_account_group)

        ctx = {'new_source_form':new_source_form,
            'root_account_group':self.root_account_group,
            'source_declaration_form':source_declaration_form}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        #Setup both forms in their default state
        new_source_form = NewSourceForm(self.root_account_group)
        source_declaration_form = SourceDeclarationForm(self.root_account_group)

        #Determine what to do based on which submit button on the page was clicked
        if 'new_declaration' in request.POST:
            source_declaration_form = SourceDeclarationForm(self.root_account_group,
                request.POST)
            if source_declaration_form.is_valid():
                declaration = source_declaration_form.save(commit = False)
                declaration.user = request.user
                declaration.save()
                messages.add_message(request, messages.SUCCESS, "Success")
                return HttpResponseRedirect(reverse_lazy(self.this_url))

        if 'new_source' in request.POST:
            new_source_form = NewSourceForm(self.root_account_group,
                request.POST)
            if new_source_form.is_valid():
                source = new_source_form.save(commit = False)
                if source.parent and not hasattr(source, 'account_group'):
                    source.account_group = source.parent.account_group
                source.save()
                messages.add_message(request, messages.SUCCESS, "Success")
                return HttpResponseRedirect(reverse_lazy(self.this_url))

        ctx = {'new_source_form':new_source_form,
            'root_account_group':self.root_account_group,
            'source_declaration_form':source_declaration_form}
        return render(request, self.template_name, ctx)


class CapitalSourcesView(DeclareSourcesView):

    form_class = None
    root_account_group = 'equity'
    this_url = 'opexa_books:capital_sources'