from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from books.models import JournalEntry, JournalEntryRule, Journal
from books.virtual.journal_entry_rules import initialize_form

class JournalForm(forms.ModelForm):

    class Meta:
        model = Journal
        exclude = []

    def clean(self):
        cleaned_data = super(JournalForm, self).clean()
        rule = cleaned_data.get("rule")
        preset = cleaned_data.get("preset")

        if rule and preset:
            raise forms.ValidationError(
                    "Please select a preset or user defined rule (not both)."
                )

        if not rule and not preset:
            raise forms.ValidationError(
                    "Please select either a preset or user defined rule."
                )



class ReadyJournalEntryForm(forms.ModelForm):

    class Meta:
        model = JournalEntry
        exclude = ['approved', 'code', 'term', 'debit_branch', 'credit_branch',
            'debit_acc', 'credit_acc']
        readonly_fields = ['rule', 'value']



class TermSheetJournalEntryForm(ReadyJournalEntryForm):

    def clean(self):
        cleaned_data = super(TermSheetJournalEntryForm, self).clean()
        rule = cleaned_data.get("rule")
        value = cleaned_data.get("value")
        
        if rule.term_sheet:
            if value > rule.term_sheet.max_value or value < rule.term_sheet.min_value:
                raise forms.ValidationError(
                    "Value outside range: Min {0} - Max {1}".format(
                        rule.term_sheet.min_value,rule.term_sheet.max_value)
                )
                
    class Meta:
        model = JournalEntry
        exclude = ['approved', 'code', 'debit_branch', 'credit_branch',
            'debit_acc', 'credit_acc']
        readonly_fields = ['rule', 'value']


            

class InitialJournalEntryForm(forms.ModelForm):

    class Meta:
        model = JournalEntry
        fields = ('rule',)
        readonly_fields = ['value']