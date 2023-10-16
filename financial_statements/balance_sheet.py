import datetime 
from calendar import monthrange

from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import Q

import books.models as book_models
from books.virtual.pdf import BalanceSheetPDFBuilder
from .base import FinancialStatement

class BalanceSheet(FinancialStatement):

    def as_dict(self, month = None, year = None):
        
        sections = {'assets':[], 'liabilities':[], 'equity':[]}

        for section_key in ['assets', 'liabilities', 'equity']:
            #Get all the account groups and their descendants
            root_section_account_groups = book_models.AccountGroup.objects.filter(
                system_account = self.system_account,
                name__contains = section_key)
            section_account_groups = book_models.AccountGroup.objects.get_queryset_descendants(
                root_section_account_groups, include_self = True)

            #Next, get all the accounts and their descendants
            rsa_kwargs = {'account_group__in':section_account_groups}
            root_section_accounts = book_models.Account.objects.filter(**rsa_kwargs)
            section_accounts = book_models.Account.objects.get_queryset_descendants(
                root_section_accounts, include_self = True)
            
            for a in section_accounts:
                if a.balance() > 0:
                    sections[section_key].append(a)

        assets_section = self.sum_section(sections['assets'],
            section_name = 'assets')
        liabilities_section = self.sum_section(sections['liabilities'],
            section_name = 'liabilities')
        capital_section = self.sum_section(sections['equity'],
            section_name = 'equity')

        today = timezone.now().date()
        bs_dict = {'entries':[], 'as_at' : today,
            'heading':"Balance Sheet as at {}".format(today.strftime('%d %b %y')),
            'assets_section':assets_section,'liabilities_section':liabilities_section,
            'capital_section':capital_section
            }
        return bs_dict


    def as_pdf(self, month = None, year = None, file_name = None):
        pl_dict = self.as_dict(month = month, year = year)
        pdf_builder = BalanceSheetPDFBuilder()
        return pdf_builder.build(pl_dict, file_name = file_name)