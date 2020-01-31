from decimal import Decimal

from books.models.config import AccountSettings

class FinancialStatement():
    def __init__(self,system_account, *args, **kwargs):
        self.system_account = system_account

    def sum_section(self, section_accounts, section_name = ''):
        sum_tot = Decimal('0.00')
        entry_list = []
        for acc in section_accounts:
            acc_bal = acc.balance()
            entry_list.append([acc, acc_bal])
            sum_tot += acc_bal

        
        return {'sum_tot':sum_tot, 'entry_list':entry_list,
        'section_name':section_name}