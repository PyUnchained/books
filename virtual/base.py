from decimal import Decimal
from collections import OrderedDict

from books.virtual.pdf import journal_to_pdf, pdf_from_preset
from books.models import JournalCreationRule, JournalEntry
from books.virtual.journals import build_table_from_preset


class VirtualObject(object):
	pass


class VirtualJournal(VirtualObject):

	def __init__(self, rule):
		self.rule = rule
		self.debt_accs = rule.include_debt_from.all()
		self.reversed_debit_accs = rule.reversed_debit_entries.all()
		self.reversed_debit_entries = JournalEntry.objects.filter(
			debit_acc__in = self.reversed_debit_accs
			).order_by('date')
		self.credit_accs = rule.include_credit_from.all()
		self.reversed_credit_accs = rule.reversed_credit_entries.all()
		self.reversed_credit_entries = JournalEntry.objects.filter(
			credit_acc__in = self.reversed_credit_accs
			).order_by('date')
		self.table = self.build_table()
		self.pdf_version()

	def build_table(self):
		debt_side = []
		credit_side = []

		#Determine the parameters to use to build the table, such as the number of columns
		#to create and their headings
		if self.rule.preset:
			print (build_table_from_preset(self))
			return build_table_from_preset(self)
			

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
		if self.rule.preset:
			return pdf_from_preset(self)
		file = journal_to_pdf(self)
		return file


	def build_side(self, side, headings, raw_entries):
		raw_entries = list(raw_entries)
		built_side = []
		entries = []
		if side == 'D':
			entry_attribute = 'debit_acc'
			reversed_entry_attribute = 'credit_acc'
			ignore_entries = list(self.reversed_debit_entries)
			include_entries = list(self.reversed_credit_entries)
		elif side == 'C':
			entry_attribute = 'credit_acc'
			reversed_entry_attribute = 'debit_acc'
			ignore_entries = list(self.reversed_credit_entries)
			include_entries = list(self.reversed_debit_entries)

		#Build the entries to use, taking into account entries that have been reversed
		for e in raw_entries:
			if e not in ignore_entries:
				entries.append(e)
		for e in include_entries:
			entries.append(e)

		entries.sort(key=lambda x: x.date, reverse=False)
		# if side == 'C':
		# 	print (raw_entries)
		# 	print (ignore_entries)
		# 	print (entries)

		# entries = raw_entries

		totals = OrderedDict()
		for h in headings:
			totals[h] = Decimal(0)

		for item in entries:
			#Change the details column depending on whether or not the double-entry
			#is based on a rule or not.
			if item.rule:
				row = [item.date,item.rule.name]
			else:
				row = [item.date,str(item)]

			if self.rule.multi_column:
				if item in include_entries:
					attr_in_use = reversed_entry_attribute
				else:
					attr_in_use = entry_attribute


				for h in headings[2:]:
					if h == getattr(item,attr_in_use).name:
						row.append(item.value)
						totals[h] += item.value
					else:
						row.append('-')
			else:
				row.append(item.value)
				totals[headings[2]] += item.value

			built_side.append(row)

		#Add the grand totals at the bottom of the side
		totals_row = ['','']
		for k,v in totals.items():
			if k in headings[2:]:
				totals_row.append(v)

		# built_side.append(totals_row)

		return (built_side, totals)
