from decimal import Decimal

from books.finance_func import fvs

TWOPLACES = Decimal(10) ** -2
SIXPLACES = Decimal(10) ** -6

def future_calculator(amount, term, term_sheet):
	"""
	Returns a list of HTML links representing the actions that can be taken on
	a given journal entry.
	"""

	if term_sheet.interest_method == 'S':
		resp = {} #This is because the demo calculator will build its table based on
		interest_rate = term_sheet.decimal_discount_rates()[0]
		discount_due = fvs(amount, interest_rate ,term)
		fees_due = amount*term_sheet.decimal_fee_rates()[0]
		payable = amount + discount_due + fees_due

		resp['discount_due'] = discount_due.quantize(TWOPLACES)
		resp['fees_due'] = fees_due.quantize(TWOPLACES)
		resp['payable'] = payable.quantize(TWOPLACES)
		resp['interest_rate'] = interest_rate.quantize(SIXPLACES)
		return resp

