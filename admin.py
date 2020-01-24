import types

from django.contrib import admin
from django import forms

from books.utils import get_account_for_user
from books.models import (Account, AccountGroup, SingleEntry, Transaction, TransactionDefinition,
	SystemAccount, DoubleEntry)
import books.forms.admin as admin_forms

# Register your models here.

class InitializedSystemAccountMixin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        return {'system_account': get_account_for_user(request.user)}

    def get_form(self, request, obj=None, **kwargs):
        print ('GETTTYYY FORM')
        form = super().get_form(request, obj, **kwargs)
        return types.new_class('FormClass',(admin_forms.RequestUserSystemAccountAdminFormMixin, form))

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

class TransactionAdmin(InitializedSystemAccountMixin):
    pass

class TransactionDefinitionAdmin(InitializedSystemAccountMixin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "debit_account" or db_field.name == "credit_account":
            kwargs["queryset"] = Account.objects.filter(
                system_account__in = request.user.systemaccount_set.all()).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AccountAdmin(InitializedSystemAccountMixin):
    list_display = ('name', 'account_group','code', 'balance')
    search_fields = ['name','account_group__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "system_account":
            kwargs["queryset"] = request.user.systemaccount_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        return {'system_account': get_account_for_user(request.user)}

    def balance(self, obj):
        return obj.balance()

class SingleEntryModelAdmin(InitializedSystemAccountMixin):
    autocomplete_fields = ['account']
    list_display = ['date', 'action', 'account', 'value', 'details']

class DoubleEntryModelAdmin(InitializedSystemAccountMixin):
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


admin.site.register(AccountGroup)
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDefinition, TransactionDefinitionAdmin)
admin.site.register(SystemAccount)
admin.site.register(SingleEntry, SingleEntryModelAdmin)
admin.site.register(DoubleEntry, DoubleEntryModelAdmin)