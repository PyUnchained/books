from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from books.models import JournalEntry, JournalEntryRule
from books.virtual.journal_entry_rules import initialize_form

class ReadyJournalEntryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReadyJournalEntryForm, self).__init__(*args, **kwargs)
        for k, v in initialize_form(self.__class__,
            self.instance.rule, return_qs = True).items():
            self.fields[k].queryset = v['queryset']

    class Meta:
        model = JournalEntry
        exclude = ('approved', 'code', 'term')

    def clean(self):
        cleaned_data = super(ReadyJournalEntryForm, self).clean()
        rule = cleaned_data.get("rule")
        value = cleaned_data.get("value")

        if rule.term_sheet:
            if value > rule.term_sheet.max_value or value < rule.term_sheet.min_value:
                raise forms.ValidationError(
                    "Value outside range: Min {0} - Max {1}".format(
                        rule.term_sheet.min_value,rule.term_sheet.max_value)
                )

class TermSheetJournalEntryForm(ReadyJournalEntryForm):


    class Meta:
        model = JournalEntry
        exclude = ('approved', 'code')
            

class InitialJournalEntryForm(forms.ModelForm):

    class Meta:
        model = JournalEntry
        fields = ('rule',)