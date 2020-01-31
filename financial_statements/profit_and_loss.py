import datetime 
from decimal import Decimal
from calendar import monthrange

from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import Q

import books.models as book_models
from books.virtual.pdf import ProfitAndLossPDFBuilder
from .base import FinancialStatement

class ProfitAndLoss(FinancialStatement):

    def as_dict(self, month = None, year = None):
        
        #Get all the accounts and their child accounts that contain information on either
        #costs or expenses
        sections = {'cost of sales':[], 'expense':[], 'income':[], 'cost of production':[]}

        for section_key in ['cost of sales', 'expense', 'income']:
            #Get all the account groups and their descendants
            root_section_account_groups = book_models.AccountGroup.objects.filter(system_account = self.system_account,
                name = section_key)
            section_account_groups = book_models.AccountGroup.objects.get_queryset_descendants(
                root_section_account_groups, include_self = True)

            #Next, get all the accounts and their descendants
            rsa_args = []
            rsa_kwargs = {'account_group__in':section_account_groups}
            if section_key == 'cost of sales':
                rsa_args.append(~Q(account_group__name = 'cost of production'))
                rsa_args.append(~Q(account_group__parent__name = 'cost of production'))

            root_section_accounts = book_models.Account.objects.filter(
                *rsa_args, **rsa_kwargs)
            if section_key == 'cost of sales':
                production_accs = book_models.Account.objects.filter(
                    account_group__name = 'cost of production')
                for a in production_accs:
                    if a.balance() > 0:
                        sections['cost of production'].append(a)

            section_accounts = book_models.Account.objects.get_queryset_descendants(
                root_section_accounts, include_self = True)
            
            for a in section_accounts:
                if a.balance() > 0:
                    sections[section_key].append(a)

        today = timezone.now().date()
        if month == None:
            month = today.month
        if year == None:
            year = today.year

        current_month_range = monthrange(year, month)
        first_day = make_aware(datetime.datetime(year, month, current_month_range[0]))
        last_day = make_aware(datetime.datetime(year, month, current_month_range[1]))

        income_section = self.sum_section(sections['income'])
        cost_of_goods_sold_section = self.sum_section(sections['cost of sales'])
        cost_of_production_section = self.sum_section(sections['cost of production'])
        gross_profit = income_section['sum_tot'] - cost_of_goods_sold_section['sum_tot'] - cost_of_production_section['sum_tot']
        expenses_section = self.sum_section(sections['expense'])
        net_profit = gross_profit - expenses_section['sum_tot']

        pl_dict = {'entries':[], 'as_at' : last_day,
            'heading':"Proft & Loss as at {}".format(last_day.strftime('%d %b %y')),
            'income_section':income_section,'cost_of_goods_sold_section':cost_of_goods_sold_section,
            'gross_profit':gross_profit,'expenses_section':expenses_section,
            'net_profit':net_profit, 'cost_of_production_section':cost_of_production_section
            }
        return pl_dict

    def as_pdf(self, month = None, year = None, file_name = None):
        pl_dict = self.as_dict(month = month, year = year)
        pdf_builder = ProfitAndLossPDFBuilder()
        return pdf_builder.build(pl_dict, file_name = file_name)