from decimal import Decimal
from collections import OrderedDict

from books.virtual.pdf import journal_to_pdf
from books.models import JournalCreationRule, JournalEntry


class VirtualObject(object):
	pass


class VirtualJournal(VirtualObject):

	def __init__(self, rule):
		self.rule = rule
		self.debt_accs = rule.include_debt_from.all()
		self.credit_accs = rule.include_credit_from.all()
		self.table = self.build_table()
		self.pdf_version()

	def build_table(self):
		debt_side = []
		credit_side = []

		#Determine the parameters to use to build the table, such as the number of columns
		#to create and their headings
		col_headings = ['Date', 'Details']
		if self.rule.multi_column:
			extra_columns = max([len(self.debt_accs), len(self.credit_accs)])
			for acc in self.debt_accs:
				col_headings.append(acc.name)
		else:
			col_headings.append('Amount')

		#Now build the table one row at a time
		debit_entries = JournalEntry.objects.filter(
			debit_acc__in = self.debt_accs).order_by('date')
		credit_entries = JournalEntry.objects.filter(
			credit_acc__in = self.credit_accs).order_by('date')

		#Now, join the two halves of the table making up the journal.
		debit_side = self.build_side('D', col_headings, debit_entries)
		debit_side_table = debit_side[0]
		credit_side = self.build_side('C', col_headings, credit_entries)
		credit_side_table = credit_side[0]
		combined_table = [col_headings+col_headings]
		for i in range(max(len(debit_side_table),len(credit_side_table))):
			combined_row = []
			for half in [debit_side_table, credit_side_table]:
				try:
					combined_row += half[i]
				except IndexError:
					blank_half = []
					for h in range(len(col_headings)):
						blank_half.append('')
					combined_row += blank_half

			combined_table.append(combined_row)

		#Add the totals at the very end
		totals_row = []
		for total_dict in [debit_side[1], credit_side[1]]:
			for k,v in total_dict.items():
				if k in col_headings[2:]:
					totals_row.append(v)
				else:
					totals_row.append('')

		combined_table.append(totals_row)
		self.col_headings = col_headings
		return combined_table

	def pdf_version(self):
		file = journal_to_pdf(self)


	def build_side(self, side, headings, entries):
		built_side = []
		if side == 'D':
			entry_attribute = 'debit_acc'
		elif side == 'C':
			entry_attribute = 'credit_acc'

		totals = OrderedDict()
		for h in headings:
			totals[h] = Decimal(0)

		for item in entries:
			row = [item.date,item.rule.name]
			if self.rule.multi_column:
				for h in headings[2:]:
					if h == getattr(item,entry_attribute).name:
						row.append(item.value)
						totals[h] += item.value
					else:
						row.append('-')
			else:
				row.append(item.value)
				totals[headings[3]] += item.value
			built_side.append(row)

		#Add the grand totals at the bottom of the side
		totals_row = ['','']
		for k,v in totals.items():
			if k in headings[2:]:
				totals_row.append(v)

		# built_side.append(totals_row)

		return (built_side, totals)
