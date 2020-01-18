from django.contrib import admin

from books.models import (Account, AccountGroup, SingleEntry, Transaction, TransactionDefinition,
	SystemAccount)

# Register your models here.

class SingleEntryInline(admin.TabularInline):
    model = SingleEntry
    exclude = ('',)
    readonly_fields = ['account', 'action', 'value']
    extra = 0
    can_delete = False

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_group', 'balance')
    search_fields = ['name','account_group__name']

    def balance(self, obj):
        return obj.balance


admin.site.register(AccountGroup)
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction)
admin.site.register(TransactionDefinition)
admin.site.register(SystemAccount)