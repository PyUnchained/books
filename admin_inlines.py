from django.contrib import admin

from books.models import JournalEntry, Account, Branch, JournalEntryAction, JournalEntryRule
# Register your models here.

class JournalEntryInline(admin.TabularInline):
	model = JournalEntry

	

class JournalEntryActionInline(admin.TabularInline):
    model = JournalEntryAction
    verbose_name = 'Transaction Effect'
    verbose_name_plural = 'Transaction Effects'
    max_num = 2
    min_num = 2