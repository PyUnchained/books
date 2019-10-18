from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField

class NewExpenseForm(forms.Form):
    description = forms.CharField(max_length = 100)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'simple-form'
        self.helper.layout = Layout(
            Div(
                Div('description', css_class='col-xs-3'),
                Div(Submit('create', 'Record'), css_class='col-xs-3'),
                css_class='row'),
        )
        super().__init__(*args, **kwargs)