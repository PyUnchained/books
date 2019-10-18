from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy

class CapitalSourcesView(View):

	def get(self, *args, **kwargs):
		pass