import datetime 
from decimal import Decimal
from calendar import monthrange

from django.utils.timezone import make_aware
from django.utils import timezone

from books.models import Account
from books.virtual.pdf import TrialBalancePDFBuilder
from .base import FinancialStatement

class TrialBalance(FinancialStatement):

    def as_dict(self, month = None, year = None):
        
        today = timezone.now().date()
        if month == None:
            month = today.month
        if year == None:
            year = today.year

        current_month_range = monthrange(year, month)
        first_day = make_aware(datetime.datetime(year, month, 1))
        last_day = make_aware(datetime.datetime(year, month, current_month_range[1]))

        trial_balance_dict = {'entries':[], 'as_at' : last_day,
            'heading':"Trial Balance as at {}".format(last_day.strftime('%d %b %y')),
            'account_list':[]
            }

        debit_total = Decimal('0.00')
        credit_total = Decimal('0.00')
        for acc in Account.objects.filter(system_account = self.system_account).order_by('account_group__name'):
            acc_balance = acc.balance(as_at = last_day, full = True)

            if acc_balance[1] > Decimal('0.00'):
                balance_entry = [acc]
                trial_balance_dict['account_list'].append(acc)
                if acc_balance[0] == 'D':
                    balance_entry.extend([acc_balance[1], ''])
                    debit_total += acc_balance[1]
                else:
                    balance_entry.extend(['', acc_balance[1]])
                    credit_total += acc_balance[1]

                trial_balance_dict['entries'].append(balance_entry)

        trial_balance_dict.update({'debit_total':debit_total,
            'credit_total':credit_total})
        return trial_balance_dict

    def as_pdf(self, month = None, year = None, file_name = None):
        tb_dict = self.as_dict(month = month, year = year)
        if tb_dict['entries'] == []:
            return None
        pdf_builder = TrialBalancePDFBuilder()
        return pdf_builder.build(tb_dict, file_name = file_name)



