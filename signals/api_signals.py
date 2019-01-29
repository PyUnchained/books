import django.dispatch

write_journal_entry_sig = django.dispatch.Signal(
	providing_args=["debit_acc", 'credit_acc', 'debit_value', 'credit_value'])
create_account_sig = django.dispatch.Signal(providing_args=['kwarg_dict'])