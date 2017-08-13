from decimal import Decimal
from collections import OrderedDict

from books.virtual.pdf import journal_to_pdf, pdf_from_preset
from books.models import JournalCreationRule, JournalEntry
from books.virtual.journal.pdf import  build_journal_from_preset
from books.exceptions import UnavailableFunctionError
from books.virtual.base import VirtualObject
from books.virtual.journal.tables import build_table_from_preset


class VirtualJournal(VirtualObject):

	def __init__(self, rule, date = None):
		self.date = None
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
		self.pdf_version = self.pdf_version()

	def build_table(self):
		if self.rule.preset:
			return build_table_from_preset(self)
		else:
			raise UnavailableFunctionError('Journals can only be created from a journal creation '
				'rule that defines a preset.')

	def pdf_version(self, test = False):
		if self.rule.preset:
			return build_journal_from_preset(self, test = False)
		else:
			raise UnavailableFunctionError('Journals can only be created from a journal creation '
				'rule that defines a preset.')


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
