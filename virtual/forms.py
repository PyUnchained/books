from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML, Field
from crispy_forms.bootstrap import TabHolder, Tab, PrependedText

from books.models import JournalEntryRule, JournalEntry

class BaseRuleBasedTransactionForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
	    self.helper = FormHelper()
	    self.helper.form_class = 'opexa_accounting_form_def'
	    self.helper.layout = Layout(

	    	TabHolder(
	    	    Tab('Record Transaction',
	    	    	Div(
	    	    	    Div('debit_acc', css_class='col-sm-4'),
	    	    	    HTML('<div class = "col-sm-4"></div>'),
	    	    	    Div('credit_acc', css_class='col-sm-4'),
	    	    	    Div('debit_branch', css_class='col-sm-4'),
	    	    	    HTML('<div class = "col-sm-4"></div>'),
	    	    	    Div('credit_branch', css_class='col-sm-4'),
	    	    	    css_class='row'),

	    	        Div(
	    	            Div('date', css_class='col-sm-4'),
	    	            Div('currency', css_class='col-sm-4'),
	    	            Div('value', css_class='col-sm-4'),
	    	            Field('rule', type="hidden"),
	    	            css_class='row'),
	    	        
	    	    )
	    	),

	        # Div(
	        #     Div('debit_acc', css_class='col-xs-3'),
	        #     Div('credit_acc', css_class='col-xs-3'),
	        #     Div('debit_branch', css_class='col-xs-3'),
	        #     Div('credit_branch', css_class='col-xs-3'),
	        #     css_class='row'),
	        # Div(
	        #     Div('date', css_class='col-xs-4'),
	        #     Div('currency', css_class='col-xs-4'),
	        #     Div('value', css_class='col-xs-4'),
	        #     css_class='row'),

	    Div(
	        Submit('create', 'Record'),
	        css_class='row',
	    )
	    )
	    super(BaseRuleBasedTransactionForm, self).__init__(*args, **kwargs)

	class Meta:
		model = JournalEntry
		exclude = ('code',)

		# widgets = {
  #           'name': forms.TextInput(attrs={'disabled': True}),
  #       }

