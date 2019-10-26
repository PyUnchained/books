from decimal import Decimal


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.auth import authenticate, login

from books.utils.auth import register_new_account
from books.models import SystemAccount, SystemUser
from books.forms.auth import AccountRegistrationForm

class AccountRegistrationView(CreateView):

    template_name = 'books/auth/register_account.html'
    form_class = AccountRegistrationForm
    model = SystemAccount

    def form_valid(self, form):

        account = register_new_account(form = form)
        return HttpResponseRedirect(
            reverse_lazy('opexa_books:new_account_login',
                kwargs = {'pk':account.pk})
        )

class AccountLoginShortCutView(View):

    def get(self,request, *args, **kwargs):
        # This view should only work if the user was redirected here from
        # the account creation view
        if 'HTTP_REFERER' in request.META:
            if reverse('opexa_books:new_account') in request.META['HTTP_REFERER']:
                user = SystemUser.objects.get(account__pk = kwargs['pk'])
                login(request, user)
                return HttpResponseRedirect(reverse('opexa_books:capital_sources'))
        
        html = "<html><body><h1>Access Denied</h1></body></html>"
        return HttpResponse(html)       