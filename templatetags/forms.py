from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
from django.forms import BaseModelFormSet


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML, Field
from crispy_forms.bootstrap import Tab, TabHolder, InlineCheckboxes


from books.models import SingleEntry

class SingleEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Div(
                Div('journal_entry', css_class='col-xs-3'),
                Div('account', css_class='col-xs-3'),
                Div('value', css_class='col-xs-3'),
                Div('action', css_class='col-xs-3'),
                css_class='col-sm-6'),

            Submit('create', 'Record')
        )

        journal_entry = kwargs.pop('journal_entry', None)
        acc_qs = kwargs.pop('acc_qs', None)
        action = kwargs.pop('action', None)
        super(SingleEntryForm, self).__init__(*args, **kwargs)

        #Set the initial queryset from the initial information supplied
        if journal_entry:
            self.fields['journal_entry'].initial = journal_entry
        if acc_qs:
            self.fields['account'].queryset = acc_qs
        if action:
            self.fields['action'].initial = action

    class Meta:
        model = SingleEntry
        fields = ['journal_entry', 'account', 'action', 'value']
        widgets = {'journal_entry':forms.HiddenInput(),
            'action':forms.HiddenInput()}

class DebitSingleEntryForm(SingleEntryForm):
    pass

class CreditSingleEntryForm(SingleEntryForm):
    pass

class SingleEntryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SingleEntryFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(

            Div(
                HTML("<div class ='col-sm-12'><h4>Entry {{ forloop.counter }}</h4></div>"),
                Field('journal_entry'),'account','value',
                css_class='inline-row formset_entry'),
        )
        self.form_tag = False


# ParcelFormSet = formset_factory(ParcleForm, extra=5,min_num=1, validate_min=True)

class DebitEntryBaseFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        try:
            if kwargs.has_key('credit_formset'):
                self.credit_formset = kwargs.pop('credit_formset')
        except:
            if 'credit_formset' in kwargs:
               self.credit_formset = kwargs.pop('credit_formset')
        super(DebitEntryBaseFormset, self).__init__(*args, **kwargs)

    def clean(self):
        from decimal import Decimal
        if hasattr(self, 'credit_formset'):
            c_tot = Decimal(0)
            d_tot = Decimal(0)

            for f in self.credit_formset:
                if f.cleaned_data:
                    c_tot += f.cleaned_data['value']
            for f in self:
                if f.cleaned_data:
                    d_tot += f.cleaned_data['value']
                    journal_entry = f.cleaned_data['journal_entry']

            #If this particular
            if journal_entry.rule.allow_single_entry:
                return

            if d_tot != c_tot:
                msg = "Debit and credit totals must match: Debit = ${0}, Credit = ${1}".format(d_tot,
                    c_tot)
                raise forms.ValidationError(msg)

DebitEntryFormset = modelformset_factory(SingleEntry,
    fields = ('journal_entry','account', 'value', 'action'),
    form = DebitSingleEntryForm, formset = DebitEntryBaseFormset, extra = 4)
CreditEntryFormset = modelformset_factory(SingleEntry,
    fields = ('journal_entry','account', 'value', 'action'),
    form = CreditSingleEntryForm, formset = BaseModelFormSet, extra = 4)