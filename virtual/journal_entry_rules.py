from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField

from books.virtual.base import VirtualJournal
from books.virtual.forms import BaseRuleBasedTransactionForm
from books.models import JournalEntryRule, JournalEntryAction, Account

def initialize_form(form_class, rule, form = None, return_qs = False):
	"""Takes a transaction rule and generates the appropriate form to input said transaction."""


	if rule:
		actions = JournalEntryAction.objects.filter(rule = rule)
		action_fields = {}
		#Determine which queryset to use and whether or not to set an initial value for it
		for a in actions:
			field_name = a.action
			if field_name == 'C':
				field_name = 'credit_acc'
			elif field_name == 'D':
				field_name = 'debit_acc'

			if a.account_type:
				qs = Account.objects.filter(account_type = a.account_type)
				initial_0 = False
			else:
				qs = Account.objects.filter(pk = a.account.pk)
				initial_0 = True
			action_fields[field_name] = {'queryset':qs, 'initial_0':initial_0}

		return action_fields
		
		#Determine the initial values to set when creating the form
		initial_data = {'rule':rule}
		for k,v in action_fields.items():
			if v['initial_0']:
				initial_data[k]= v['queryset'][0].pk

		#Only create the actual form if an instance of the form has not
		#been supplied already
		if form == None:
			form = form_class(initial = initial_data)

		#Override the default querysets as defined by the rules
		for k,v in action_fields.items():
			form.fields[k].queryset = v['queryset']
			# if v['initial_0']:
			# 	form.fields[k].disabled = True
	else:
		initial_data = {'rule':rule}
		form = form_class(initial = initial_data)

	return form

def build_journal(rule):
	vj = VirtualJournal(rule)
	fn = '{0} ({1}).pdf'.format(rule, timezone.now())
	rule.latest_pdf.save(fn, vj.pdf_version())
	vj.rule = rule
	return vj