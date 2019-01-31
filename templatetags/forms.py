from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
from django.forms import BaseModelFormSet


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML, Field
from crispy_forms.bootstrap import Tab, TabHolder, InlineCheckboxes
from django_select2.forms import Select2Widget


from books.models import SingleEntry, Account

class SingleEntryForm(forms.ModelForm):
    debit = forms.DecimalField(decimal_places = 2)
    credit = forms.DecimalField(decimal_places = 2)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Div(
                # Div('journal_entry', css_class='col-xs-3'),
                Div('account', css_class='col-xs-12'),
                # Div('value', css_class='col-xs-3'),
                # Div('action', css_class='col-xs-3'),
                css_class='col-sm-12'),

            Submit('create', 'Record')
        )

        journal_entry = kwargs.pop('journal_entry', None)
        acc_qs = kwargs.pop('acc_qs', None)
        action = kwargs.pop('action', None)
        super(SingleEntryForm, self).__init__(*args, **kwargs)
        self.fields['account'].required = True
        self.fields['debit'].required = False
        self.fields['credit'].required = False

        

        #Set the initial queryset from the initial information supplied
        # if journal_entry:
        #     self.fields['journal_entry'].initial = journal_entry
        if acc_qs:
            self.fields['account'].queryset = acc_qs
        else:
            self.fields['account'].queryset = Account.objects.all()
        if action:
            self.fields['action'].initial = action

    def clean(self):
        debit = self.cleaned_data.get("debit")
        credit = self.cleaned_data.get("credit")
        if credit == None and debit == None:
            self.add_error('credit', forms.ValidationError("Amount?"))
            self.add_error('debit', forms.ValidationError("Amount?"))
        elif credit != None and debit != None:
            if credit > Decimal('0.00') and debit > Decimal('0.00'):
                self.add_error('credit', forms.ValidationError("Choose one."))
                self.add_error('debit', forms.ValidationError("Choose one."))

    class Meta:
        model = SingleEntry
        fields = ['account', 'action', 'value']
        widgets = {
            'account':Select2Widget()}

class DebitSingleEntryForm(SingleEntryForm):
    pass

class CreditSingleEntryForm(SingleEntryForm):
    pass

class SingleEntryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SingleEntryFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(

            Div(
                
                Field('journal_entry'),'account','value',
                css_class='inline-row formset_entry'),
            Div(
                HTML("<div class ='col-sm-12'><h4>Entry {{ forloop.counter }}</h4></div>"),
                css_class='col-sm-12'),
            Div(
                HTML("<div class ='col-sm-12'><h4>Entry {{ forloop.counter }}</h4></div>"),
                Div('account', css_class='col-xs-6'),
                Div('credit', css_class='col-xs-3'),
                Div('debit', css_class='col-xs-3'),
                css_class='col-sm-12'),
        )
        self.form_tag = False

class GeneralDoubleEntryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(GeneralDoubleEntryFormSetHelper, self).__init__(*args, **kwargs)
        # self.template = 'crispy_forms/bootstrap3/general_double_entry_table_inline_formset.html'
        self.add_input(Submit("submit", "Save"))
        self.layout = Layout(
            Div(
                Div(
                    Div('account', css_class='col-sm-6'),
                    Div('credit', css_class='col-sm-3'),
                    Div('debit', css_class='col-sm-3'),
                    css_class='row'),
                Div(
                    Div('journal_entry', css_class='col-sm-12'),
                    css_class='row'),

                css_class ='container')
            
        )
        # self.form_tag = False


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

class GeneralDoubleEntryBaseFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(GeneralDoubleEntryBaseFormset, self).__init__(*args, **kwargs)

    def clean(self):
        #Don't validate unless each form is valid on its own
        if any(self.errors):
            return

        c_tot = Decimal(0)
        d_tot = Decimal(0)
        for f in self.forms:
            
            try:
                c_tot += f.cleaned_data['credit']
            except:
                pass

            try:
                d_tot += f.cleaned_data['debit']
            except:
                pass


        if d_tot != c_tot:
            msg = "Debit = ${0}, Credit = ${1}".format(d_tot,
                c_tot)
            raise forms.ValidationError(msg)



GeneralDoubleEntryFormSet = modelformset_factory(
    SingleEntry, form = SingleEntryForm, formset =GeneralDoubleEntryBaseFormset,
    extra = 0, validate_min=True, min_num = 2,
    fields = ('account', 'debit', 'credit'),
    widgets = {
            'account':Select2Widget()})
DebitEntryFormset = modelformset_factory(SingleEntry,
    fields = ('account', 'value', 'action'),
    form = DebitSingleEntryForm, formset = DebitEntryBaseFormset, extra = 4)
CreditEntryFormset = modelformset_factory(SingleEntry,
    fields = ('account', 'value', 'action'),
    form = CreditSingleEntryForm, formset = BaseModelFormSet, extra = 4)