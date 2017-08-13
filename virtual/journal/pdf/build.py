from .presets import trial_balance_preset, cash_book_preset, balace_sheet_preset, profit_and_loss_preset

def build_journal(virtual_journal):
	return None

def build_journal_from_preset(virtual_journal, test = False):
	if virtual_journal.rule.preset == 'TB':
		return trial_balance_preset(virtual_journal)
	if virtual_journal.rule.preset == 'CB':
		return cash_book_preset(virtual_journal)
	if virtual_journal.rule.preset == 'BS':
		return balace_sheet_preset(virtual_journal)
	if virtual_journal.rule.preset == 'PL':
		return profit_and_loss_preset(virtual_journal)
	return None