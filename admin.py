from django.contrib import admin

from books.admin_inlines import JournalEntryActionInline, JournalEntryInline
from books.models import (JournalEntry, Account, Branch, JournalEntryAction,
    JournalEntryRule, Journal, JournalCreationRule, AccountType, OpexaBooksSystem,
    TermSheet, Upload, SingleEntry, AccountSubType)
from books.admin_forms import (InitialJournalEntryForm, ReadyJournalEntryForm, TermSheetJournalEntryForm,
    JournalForm)

# Register your models here.

class SingleEntryInline(admin.TabularInline):
    model = SingleEntry
    exclude = ('',)
    readonly_fields = ['journal_entry', 'account', 'action', 'value']
    extra = 0
    can_delete = False

class AccountTypeAdmin(admin.ModelAdmin):
    pass

class JournalAdmin(admin.ModelAdmin):
    form = JournalForm
    readonly_fields = ['link']
    fields = ['link', ('code', 'name'),'rule']

    def link(self, obj):
        return obj.link

    link.allow_tags = True

    class Media:
        css = {
          'all': ('css/extra_admin.css',)
        }

class OpexaBooksSystemAdmin(admin.ModelAdmin):
    pass

class JournalCreationRuleAdmin(admin.ModelAdmin):
    filter_horizontal = ['include_debt_from', 'include_credit_from', 'reversed_debit_entries',
        'reversed_credit_entries']
    list_display = ['name', 'preset', 'date_from', 'date_to']
    fieldsets = [
    ('Basic', {'fields':['name', 'preset', ('date_from', 'date_to')]}),
    ]



class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'approved', 'date', 'value', 'currency')
    exclude = []
    readonly_fields = ['value']
    search_fields = ('debit_acc__name', 'debit_acc__account_type',
        'credit_acc__name', 'credit_acc__account_type', 'currency', 'rule__name')
    inlines = [SingleEntryInline]

    class Media:
        css = {
          'all': ('css/extra_admin.css',)
        }
        js = ('js/jquery-2.2.4.js','js/jquery.bpopup.min.js','js/books_admin_popup.js',
            'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css')

    def value(self, obj):
        return obj.value

    def get_form(self, request, obj=None, **kwargs):
        form_found = False
        if obj:
            if obj.rule:
                if obj.rule.term_sheet:
                    kwargs['form'] = TermSheetJournalEntryForm
                    self.exclude = TermSheetJournalEntryForm.Meta.exclude
                    self.readonly_fields = TermSheetJournalEntryForm.Meta.readonly_fields
                    form_found = True
                else:
                    kwargs['form'] = ReadyJournalEntryForm
                    self.exclude = ReadyJournalEntryForm.Meta.exclude
                    self.readonly_fields = ReadyJournalEntryForm.Meta.readonly_fields
                    form_found = True
        if not form_found:
            kwargs['form'] = InitialJournalEntryForm
            self.readonly_fields = []
            self.exclude = []



        return super(JournalEntryAdmin, self).get_form(request, obj, **kwargs)

    def name(self, obj):
        return str(obj)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'sub_type', 'balance')
    search_fields = ['name','account_type__name', 'sub_type__name']

    def balance(self, obj):
        return obj.balance

class BranchAdmin(admin.ModelAdmin):
    pass


class JournalEntryActionAdmin(admin.ModelAdmin):
    pass

class JournalEntryRuleAdmin(admin.ModelAdmin):
    fields = ('name', ('term_sheet', 'allow_single_entry'))
    inlines = [JournalEntryActionInline]


admin.site.register(AccountType, AccountTypeAdmin)
# admin.site.register(Journal, JournalAdmin)
# admin.site.register(JournalCreationRule, JournalCreationRuleAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(Account, AccountAdmin)
# admin.site.register(Branch, BranchAdmin)
# admin.site.register(JournalEntryAction, JournalEntryActionAdmin)
# admin.site.register(JournalEntryRule, JournalEntryRuleAdmin)
# admin.site.register(OpexaBooksSystem, OpexaBooksSystemAdmin)
# admin.site.register(TermSheet)
# admin.site.register(Upload)
# admin.site.register(AccountSubType)
# admin.site.register(SingleEntry)