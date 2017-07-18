from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist


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
                css_class='col-sm-6'),

            Submit('create', 'Record')
        )
        super(SingleEntryForm, self).__init__(*args, **kwargs)

        #Set the initial queryset from the initial information supplied
        if 'initial' in kwargs.keys():
            if 'queryset' in kwargs['initial'].keys():
                self.fields['account'].queryset = kwargs['initial']['queryset']

    class Meta:
        model = SingleEntry
        fields = '__all__'
        widgets = {'journal_entry':forms.HiddenInput()}

class DebitSingleEntryForm(SingleEntryForm):
    pass

class CreditSingleEntryForm(SingleEntryForm):
    pass

class SingleEntryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SingleEntryFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(

            Div(
                HTML("<div class ='col-sm-12'><h4>Account {{ forloop.counter }}</h4></div>"),
                Field('journal_entry'),'account','value',
                css_class='inline-row formset_entry'),
        )
        # self.layout = Layout(
        #     'owner',
        # )
        # self.render_required_fields = True
        self.form_tag = False


# ParcelFormSet = formset_factory(ParcleForm, extra=5,min_num=1, validate_min=True)