from decimal import Decimal

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import check_password, make_password, is_password_usable

from books.conf import chart_of_accounts_setup
from books.models.config import SystemAccount
from books.forms.auth import AccountRegistrationForm

class AccountRegistrationView(View):

    template_name = 'books/auth/register_account.html'

    def get(self, request, *args, **kwargs):
        form = AccountRegistrationForm()
        ctx = {'form':form}
        return render(request, self.template_name, ctx)

