from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML

from books.models.auth import SystemAccount

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length = 200,
        widget = forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'books_form'
        self.helper.layout = Layout(

            Div(
                Div('email', css_class='col-sm-12'),
                css_class='row'),

            Div(
                Div('password', css_class='col-sm-12'),
                css_class='row'),

            Div(
                Submit('login', 'Login'),
                css_class='row',
            )
        )
        super().__init__(*args, **kwargs)

class AccountRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length = 200,
        widget = forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'books_form'
        self.helper.layout = Layout(

            Div(
                Div('name', css_class='col-sm-6'),
                Div('email', css_class='col-sm-6'),
                css_class='row'),

            Div(
                Div('confirm_password', css_class='col-sm-6'),
                css_class='row'),

            Div(
                Submit('new_account', 'Create'),
                css_class='row',
            )
        )
        super().__init__(*args, **kwargs)

    class Meta():
        model = SystemAccount
        fields = ['name', 'email']

    class Media:
        js = ['books/js/forms/new_account.js']

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        #Check no-one else has used the same email address already
        same_email_accounts = SystemAccount.objects.filter(
            email = cleaned_data['email']).count()
        
        if same_email_accounts > 0:
            raise ValidationError('Email address already taken (have you forgotten your password?)')
