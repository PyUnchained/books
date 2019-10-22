from decimal import Decimal

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages


from books.models import Account, AccountGroup, DeclaredSource
from books.forms import NewSourceForm, SourceDeclarationForm

class DashboardView(View):
    template_name = 'books/dashboard/home.html'
    def get(self, request, *args, **kwargs):
        ctx = {}
        return render(request, self.template_name, ctx)