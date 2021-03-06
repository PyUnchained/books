import operator 
import functools

from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.apps import apps

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML

from books.models import Account, AccountGroup, DeclaredSource

app_label, model_name = settings.AUTH_USER_MODEL.split('.')
UserModel = apps.get_model(app_label=app_label, model_name=model_name)

def related_acc_groups(root_account_group, system_account):
    if root_account_group == 'liability':
        root_groups = AccountGroup.objects.filter(
            name__in = ['current liabilities', 'long-term liabilities', 'liability'],
            system_account = system_account)
        related_groups = AccountGroup.objects.get_queryset_descendants(
            root_groups, include_self = True)
    elif root_account_group == 'assets':
        root_groups = AccountGroup.objects.filter(
            name__in = ['current assets', 'long-term assets'],
            system_account = system_account)
        related_groups = AccountGroup.objects.get_queryset_descendants(
            root_groups, include_self = True)
    else:
        root_group_obj = AccountGroup.objects.get(name = root_account_group,
            system_account = system_account)
        related_groups = root_group_obj.get_descendants(include_self = True)

    return related_groups

class InitializeIntegratedAccountForm(forms.Form):

    def __init__(self, request_user = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'books_form'
        self.helper.form_action = reverse_lazy('opexa_books:initialize_integrated_package')
        self.helper.layout = Layout(

         

            Div(
                Submit('initalize', 'Initialize'),
                css_class='row',
            )
        )
        


class NewSourceForm(forms.ModelForm):
    def __init__(self, root_account_group = None, system_account = None, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'books_form'
        self.helper.layout = Layout(

            Div(
                Div('name', css_class='col-sm-3'),
                Div('parent', css_class='col-sm-3'),
                Div('account_group', css_class='col-sm-3'),
                css_class='row'),

            Div(
                Submit('new_source', 'Create'),
                css_class='row',
            )
        )
        super().__init__(*args, **kwargs)

        # root_group_obj = AccountGroup.objects.get(name = root_account_group)
        related_groups = related_acc_groups(root_account_group, system_account)
        self.fields['account_group'].queryset = related_groups
        self.fields['parent'].queryset = Account.objects.filter(
            account_group__in = related_groups,
            system_account = system_account)


    class Meta:
        model = Account
        fields = ['name', 'parent', 'account_group']

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if not cleaned_data['parent'] and cleaned_data['account_group'] == None:
            raise ValidationError('''No parent account selected. Please choose an account group 
                or parent account.''')
        return cleaned_data

class SourceDeclarationForm(forms.ModelForm):

    def __init__(self, root_account_group, system_account, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'books_form'
        self.helper.layout = Layout(

            Div(
                Div('account', css_class='col-sm-3'),
                Div('debit', css_class='col-sm-2'),
                Div('credit', css_class='col-sm-2'),
                Div('details', css_class='col-sm-3'),
                Div('date', css_class='col-sm-2'),
                css_class='row'),

            Div(
                Submit('new_declaration', 'Declare'),
                css_class='row',
            )
        )
        super().__init__(*args, **kwargs)
        related_groups = related_acc_groups(root_account_group, system_account)
        self.fields['account'].queryset = Account.objects.filter(
            account_group__in = related_groups,
            system_account = system_account)
        self.fields['date'].input_formats=settings.DATE_INPUT_FORMATS

    class Meta:
        model = DeclaredSource
        fields = ['account', 'debit', 'credit', 'date', 'details']

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if cleaned_data['debit'] == None and cleaned_data['credit'] == None:
            raise ValidationError('Please enter either a debit or credit value.')
        elif cleaned_data['debit'] != None and cleaned_data['credit'] != None:
            raise ValidationError('Please enter either a debit or credit value, not both.')
        return cleaned_data
