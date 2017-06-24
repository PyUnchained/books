from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField


from books.models import JournalEntry, JournalEntryRule

class JournalEntryRuleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'opexa_accounting_form_def'
        self.helper.layout = Layout(

            Div(
                Div('name', css_class='col-xs-3'),
                Div('display_template', css_class='col-xs-3'),
                css_class='row'),

        Div(
            Submit('create', 'Record'),
            css_class='row',
        )
        )
        super(JournalEntryRuleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JournalEntryRule
        fields = '__all__'

class JournalEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'opexa_accounting_form_def'
        self.helper.layout = Layout(

            Div(
                Div('debit_acc', css_class='col-xs-3'),
                Div('debit_branch', css_class='col-xs-3'),
                Div('credit_acc', css_class='col-xs-3'),
                Div('credit_branch', css_class='col-xs-3'),
                css_class='row'),

        Div(
            Submit('create', 'Record'),
            css_class='row',
        )
        )
        super(JournalEntryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JournalEntry
        exclude = ('approved',)