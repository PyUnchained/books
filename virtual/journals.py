from decimal import Decimal

from django.utils import timezone

from books.models import Account

def build_table_from_preset(virtual_journal):
	if virtual_journal.rule.preset == 'TB':
		return trial_balance_table_preset(virtual_journal)
	if virtual_journal.rule.preset == 'BS':
		return balance_sheet_table_preset(virtual_journal)
	
def balance_sheet_table_preset(virtual_journal):
	virtual_journal.col_headings = ['Date', 'Details', 'Amount'] + ['Date', 'Details', 'Amount']
	table = []
	table.append(virtual_journal.col_headings)
	table.append([virtual_journal.date, '', '', virtual_journal.date, '', ''])

	gp = Decimal(0)
	purchases_accs = Account.objects.filter(account_type__name = 'PU')
	revenue_accs = Account.objects.filter(account_type__name = 'R')
	expense_accs = Account.objects.filter(account_type__name = 'E')
	for acc in purchases_accs:
		gp -= acc.balance_as_at()
	for acc in revenue_accs:
		gp += acc.balance_as_at()

	for num, acc in enumerate(expense_accs):
		row = ['', str(acc), scc.balance_as_at()]
		



def trial_balance_table_preset(virtual_journal):
	virtual_journal.col_headings = ['Details', 'Dr', 'Cr']
	table = []
	table.append(virtual_journal.col_headings)
	accounts = Account.objects.all()
	cr_tot = Decimal('0')
	db_tot = Decimal('0')
	for a in accounts:
		use_record = True
		record = [a.name]
		balance = a.debit_minus_credit_balance(
			date__gte = virtual_journal.rule.after_date,
			date__lte = virtual_journal.rule.before_date)

		if balance < 0:
			record += ['-', abs(balance)]
			cr_tot += abs(balance)
		elif balance > 0:
			record += [balance, '-']
			db_tot += abs(balance)
		else:
			record += ['0.00', '0.00']

		if use_record:
			table.append(record)

	table.append(['', db_tot, cr_tot])
	return table
