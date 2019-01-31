import django.dispatch

double_entry_sig = django.dispatch.Signal(
	providing_args=["debit_acc", 'credit_acc', 'value', 'date',
	'debit_details', 'credit_details'])
create_account_sig = django.dispatch.Signal(providing_args=['kwarg_dict'])