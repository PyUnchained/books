import types

from django.contrib import admin
from django import forms

from books.utils import get_account_for_user
from books.models import (Account, AccountGroup, SingleEntry, Transaction, TransactionDefinition,
	SystemAccount, DoubleEntry)
import books.forms.admin as admin_forms
from books.utils.auth import get_account_for_user

def save_all(modeladmin, request, queryset):
    for item in queryset:
        item.save()

class SaveAllActionMixin():
    actions = [save_all]

class FilterBySystemAccountMixin():

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(system_account=get_account_for_user(request.user))

class InitializedSystemAccountMixin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        return {'system_account': get_account_for_user(request.user)}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return types.new_class('FormClass',
            (admin_forms.RequestUserSystemAccountAdminFormMixin, form))

class DoubleEntryInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        debit_value = 0
        credit_value = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    if form.cleaned_data['action'] == 'D':
                        debit_value += form.cleaned_data['value']
                    else:
                        credit_value += form.cleaned_data['value']
            except AttributeError:
                pass
                
        if credit_value != debit_value:
            raise forms.ValidationError('Debit {} and Credit {} totals must match!'.format(
                debit_value, credit_value))

class SingleEntryInline(admin.TabularInline):
    model = SingleEntry
    fields = ['account', 'action', 'value' ]
    autocomplete_fields = ['account']
    extra = 2
    formset = DoubleEntryInlineFormset

class TransactionAdmin(SaveAllActionMixin, InitializedSystemAccountMixin):
    pass

class TransactionDefinitionAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    list_display = ['description', 'system_account', 'short_code']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AccountGroupAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    search_fields = ['name', 'parent__name']
    autocomplete_fields = ['parent']
    list_display = ['name', 'parent']

class AccountAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    list_display = ('name', 'account_group','code', 'balance')
    search_fields = ['name','account_group__name', 'parent__name']
    autocomplete_fields = ['parent', 'account_group']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        return {'system_account': get_account_for_user(request.user)}

    def balance(self, obj):
        return obj.balance()

class SingleEntryModelAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    autocomplete_fields = ['account']
    list_display = ['date', 'action', 'account', 'value', 'details', 'double_entry']

class DoubleEntryModelAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    inlines = [SingleEntryInline]
    list_display = ['date', 'details']

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            #Assume that objects with a user field are meant to be
            #linked to the user making the request.
            instance.system_account = get_account_for_user(request.user)
            instance.date = instance.double_entry.date
            instance.details = instance.double_entry.details
            instance.save()
        formset.save_m2m()

class TransactionAdmin(SaveAllActionMixin, FilterBySystemAccountMixin, InitializedSystemAccountMixin):
    list_display = ['definition', 'date', 'value', 'details']
    fields = ['definition', 'date', 'value', 'details', 'double_entry_record']
    readonly_fields=['double_entry_record']

admin.site.register(AccountGroup, AccountGroupAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(SystemAccount)
admin.site.register(SingleEntry, SingleEntryModelAdmin)
admin.site.register(DoubleEntry, DoubleEntryModelAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDefinition, TransactionDefinitionAdmin)