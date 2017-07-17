from books.virtual.finance import *

def calculate_interest(journal_entry, days):
	rule = journal_entry.rule
	ts = rule.term_sheet
	if ts.interest_method == 'S':
		return fvs(journal_entry.value, discount_rate/365.00, days)
