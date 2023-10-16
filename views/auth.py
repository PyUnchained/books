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
from django.apps import apps

from books.utils.auth import register_new_account
from books.models import SystemAccount
from books.forms.auth import AccountRegistrationForm, LoginForm

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

        if 'HTTP_REFERER' in request.META:
            if reverse('opexa_books:new_account') in request.META['HTTP_REFERER']:
                app_label, model_name = settings.AUTH_USER_MODEL.split('.')
                UserModel = apps.get_model(app_label=app_label,
                    model_name=model_name)
                acc = SystemAccount.objects.get(pk = kwargs['pk'])
                user = acc.users.all()[0]
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect(reverse('opexa_books:capital_sources'))
        
        html = "<html><body><h1>Access Denied</h1></body></html>"
        return HttpResponse(html)

class LoginView(View):
    template_name = 'books/auth/login.html'

    def get(self,request, *args, **kwargs):
        form = LoginForm()
        ctx = {'form':form}
        return render(request, self.template_name, ctx)

    def post(self,request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username = form.cleaned_data['email'],
                password = form.cleaned_data['password'])
            if user:
                login(request, user)
                if user.account.initial_setup_done:
                    return HttpResponseRedirect(reverse('opexa_books:dashboard'))
                else:
                    return HttpResponseRedirect(reverse('opexa_books:capital_sources'))
            else:
                messages.add_message(request, messages.ERROR, "Bad username/password")

        ctx = {'form':form}
        return render(request, self.template_name, ctx)      