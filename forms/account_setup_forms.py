import operator 
import functools

from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q 


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML

from books.models import Account, AccountGroup, DeclaredSource

def related_acc_groups(root_account_group):
    if root_account_group == 'liability':
        root_groups = AccountGroup.objects.filter(
            name__in = ['current liabilities', 'long-term liabilities', 'liability'])
        related_groups = AccountGroup.objects.get_queryset_descendants(
            root_groups, include_self = True)
    elif root_account_group == 'assets':
        root_groups = AccountGroup.objects.filter(
            name__in = ['current assets', 'long-term assets'])
        related_groups = AccountGroup.objects.get_queryset_descendants(
            root_groups, include_self = True)
    else:
        root_group_obj = AccountGroup.objects.get(name = root_account_group)
        related_groups = root_group_obj.get_descendants(include_self = True)

    return related_groups




class NewSourceForm(forms.ModelForm):
    def __init__(self, root_account_group, *args, **kwargs):
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
        related_groups = related_acc_groups(root_account_group)
        self.fields['account_group'].queryset = related_groups
        self.fields['parent'].queryset = Account.objects.filter(
            account_group__in = related_groups)


    class Meta:
        model = Account
        fields = ['name', 'parent', 'account_group']

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if not cleaned_data['parent'] and cleaned_data['account_group'] == None:
            raise ValidationError('No parent account selected, so please select an account group.')
        return cleaned_data

class SourceDeclarationForm(forms.ModelForm):

    def __init__(self, root_account_group, *args, **kwargs):
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

        # root_group_obj = AccountGroup.objects.get(name = root_account_group)
        related_groups = related_acc_groups(root_account_group)
        self.fields['account'].queryset = Account.objects.filter(
            account_group__in = related_groups)

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