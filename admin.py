from django.contrib import admin

from books.admin_inlines import JournalEntryActionInline, JournalEntryInline
from books.models import (JournalEntry, Account, Branch, JournalEntryAction,
	JournalEntryRule, Journal, JournalCreationRule, AccountType)

# Register your models here.

class AccountTypeAdmin(admin.ModelAdmin):
	pass

class JournalAdmin(admin.ModelAdmin):
	pass

class JournalCreationRuleAdmin(admin.ModelAdmin):
	filter_horizontal = ['include_debt_from', 'include_credit_from']

class JournalEntryAdmin(admin.ModelAdmin):
	list_display = ('name', 'approved', 'date', 'value', 'currency',
		'debit_acc', 'credit_acc')
	search_fields = ('debit_acc__name', 'debit_acc__account_type',
		'credit_acc__name', 'credit_acc__account_type', 'currency', 'rule__name')

	def name(self, obj):
		return str(obj)

class AccountAdmin(admin.ModelAdmin):
	list_display = ('name', 'account_type', 'balance')
	search_fields = ['name','account_type']

	def balance(self, obj):
		return obj.balance

class BranchAdmin(admin.ModelAdmin):
	pass


class JournalEntryActionAdmin(admin.ModelAdmin):
	pass

class JournalEntryRuleAdmin(admin.ModelAdmin):
	fields = ('name',)
	inlines = [JournalEntryActionInline]


admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(JournalCreationRule, JournalCreationRuleAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(JournalEntryAction, JournalEntryActionAdmin)
admin.site.register(JournalEntryRule, JournalEntryRuleAdmin)