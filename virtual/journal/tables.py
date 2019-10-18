from decimal import Decimal
from collections import OrderedDict

from django.utils import timezone
from django.db.models import Q

from books.models import Account, SingleEntry

def build_table_from_preset(virtual_journal):
    if virtual_journal.rule.preset == 'TB':
        return trial_balance_table_preset(virtual_journal)
    if virtual_journal.rule.preset == 'BS':
        return balance_sheet_table_preset(virtual_journal)
    if virtual_journal.rule.preset == 'CB':
        return cash_book_table_preset(virtual_journal)
    if virtual_journal.rule.preset == 'PL':
        return profit_and_loss_table_preset(virtual_journal)

def sum_account_balances(qs, date_from = None, date_to = None):
    ans = Decimal('0.00')
    for acc in qs:
        ans += acc.balance_between(date__gte = date_from,
            date__lte = date_to)
    return ans

def columnar_account_table(virtual_journal, accounts):

    #First, start by compiling information on all of the entries
    #that appear either on the debit or credit side.
    sides = ['D', 'C']
    raw_data = OrderedDict()
    side_tables = []
    totals = OrderedDict()
    for side in sides:
        #Determine the heading to set
        built_side = OrderedDict()
        built_side['Date'] = []
        built_side['Details'] = []
        column_totals = OrderedDict()

        #If more than one account is supplied assume it should be mulit-column
        if len(accounts) > 1:
            for acc in accounts:
                acc_name = str(acc)
                built_side[acc_name] = []
                column_totals[acc_name] = Decimal('0.00')



        #If only one is supplied, assume it will be a traditional
        #T-account
        else:
            built_side['Amount'] = []

        
        entries = SingleEntry.objects.filter(account__in = accounts,
            action = side)
        for e in entries:
            built_side['Date'].append(e.journal_entry.date)
            built_side['Details'].append(e.journal_entry)

            #Place value in correct column depending on whether it is
            #a multi-column or single-column account
            acc_name = str(e.account)
            if acc_name in built_side.keys():
                #Append value in correct column and add the value
                #to the total for that column
                built_side[acc_name].append(e.value)
                column_totals[acc_name] += e.value

                #Append a '-' to all other columns, except the date and details
                for k in built_side.keys():
                    if k != acc_name and k not in ['Date', 'Details']:
                        built_side[k].append('-')
            else:
                built_side['Amount'].append(e.value)
                column_totals['Amount'] += e.value

        
        raw_data[side] = built_side
        totals[side] = column_totals


    complete_table = []

    #Add headings to table and determine the longest side of the table
    headings = []
    longest_side = 0
    for side in raw_data.keys():
        for h in raw_data[side].keys():
            headings.append(h)
            length = len(raw_data[side][h])
            if length > longest_side:
                longest_side = length
    complete_table.append(headings)

    #Add all the other information in the table, except totals
    for row_num in range(longest_side):
        row = []
        for side in raw_data.keys():
            for h in raw_data[side].keys():
                try:
                    row.append(raw_data[side][h][row_num])
                except IndexError:
                    row.append('-')
        complete_table.append(row)

    #Finally, add the totals to the bottom of the page and bring values
    #forward
    totals_row = []
    for side in totals.keys():
        for i in range(2):
            totals_row.append('')
        for t in totals[side]:
            totals_row.append(totals[side][t])
    complete_table.append(totals_row)

    bf_row = []
    debit_totals = totals['D']
    credit_totals = totals['C']
    for i in range(2):
        bf_row.append('')
    for k in debit_totals:
        debit_tot = debit_totals[k]
        credit_tot = credit_totals[k]
        tot = debit_tot - credit_tot
        if tot > Decimal('0.00'):
            bf_row.append(tot)
        else:
            bf_row.append('-')

    for i in range(2):
        bf_row.append('')
    for k in credit_totals:
        debit_tot = debit_totals[k]
        credit_tot = credit_totals[k]
        tot = debit_tot - credit_tot
        if tot < Decimal('0.00'):
            bf_row.append(abs(tot))
        else:
            bf_row.append('-')
    complete_table.append(bf_row)

    return complete_table


def cash_book_table_preset(virtual_journal):
    accounts = Account.objects.filter(
        sub_type = 'cash and cash equivalents')
    return columnar_account_table(virtual_journal, accounts)

def profit_and_loss_table_preset(virtual_journal):
    table = []
    space = ['', '', '']
    date_from = virtual_journal.rule.date_from
    date_to = virtual_journal.rule.date_to
    print (date_from, date_to)

    income_accs = Account.objects.filter(account_type = 'income')
    cost_of_sales_accs = Account.objects.filter(Q(account_type = 'cost of sales'),
        ~Q(code = '4460'))
    expense_accs = Account.objects.filter(account_type = 'expense')
    closing_stock_accs = Account.objects.filter(code = '4460')
    drawings_accs = Account.objects.filter(code = '3010')

    income_amt = sum_account_balances(income_accs,
        date_from = date_from, date_to = date_to)
    cost_of_sales_amt = sum_account_balances(cost_of_sales_accs,
        date_from = date_from, date_to = date_to)
    expense_amt = sum_account_balances(expense_accs,
        date_from = date_from, date_to = date_to)
    closing_stock_amt = sum_account_balances(closing_stock_accs,
        date_from = date_from, date_to = date_to)
    drawings_amt = sum_account_balances(drawings_accs,
        date_from = date_from, date_to = date_to)
    net_profit_amt = income_amt - (cost_of_sales_amt - closing_stock_amt) - expense_amt

    #Fixed assets section
    table.append(['Income', '', income_amt])
    table.append(['Less cost of sales', '', ''])

    for acc in cost_of_sales_accs:
        amt = acc.balance_between(date__gte = date_from,
            date__lte = date_to)
        if amt > Decimal('0'):
            table.append([str(acc), amt, ''])
    table.append(['',cost_of_sales_amt, ''])
    table.append(['Less closing stock', closing_stock_amt, ''])
    cost_of_sales_less_stock = cost_of_sales_amt - closing_stock_amt
    table.append(['', '', cost_of_sales_less_stock])
    gross_profit = income_amt - cost_of_sales_less_stock
    table.append(['Gross profit', '', gross_profit])
    table.append(['Less', '', ''])
    for acc in expense_accs:
        amt = acc.balance_between(date__gte = date_from,
            date__lte = date_to)
        if amt > Decimal('0'):
            table.append([str(acc), amt, ''])
    table.append(['', '', expense_amt])
    table.append(['Net Profit', '', net_profit_amt])
    return table

    # #Current assets section
    # table.append(['Current Assets', '', ''])
    # for acc in current_asset_accs:
    #     amt = acc.balance_between(date__gte = date_from,
    #         date__lte = date_to)
    #     if amt > Decimal('0'):
    #         table.append([str(acc), amt, ''])
    #         current_asset_amt += amt
    # table.append(['', current_asset_amt, ''])
    # table.append(['Less current liabilities', current_liability_amt, ''])
    # assets_less_liabilities_amt = current_asset_amt-current_liability_amt
    # table.append(['', '', assets_less_liabilities_amt])
    # table.append(['', '', fixed_asset_amt + assets_less_liabilities_amt])
    # table.append(space)

    # #Capital Section
    # table.append(['Capital', '', ''])
    # for acc in capital_accs:
    #     amt = acc.balance_between(date__gte = date_from,
    #         date__lte = date_to)
    #     if amt > Decimal('0'):
    #         table.append([str(acc), '', amt])
    #         capital_amt += amt
    # table.append(['Add Net Profit*', '', net_profit_amt])
    # add_net_profit_amt = net_profit_amt + capital_amt
    # table.append(['', '', add_net_profit_amt])
    # table.append(['Less Drawings', '', drawings_amt])
    # less_drawing_amt = add_net_profit_amt - drawings_amt
    # table.append(['', '', less_drawing_amt])
    # table.append(space)

def balance_sheet_table_preset(virtual_journal):
    table = []
    space = ['', '', '']
    date_from = virtual_journal.rule.date_from
    date_to = virtual_journal.rule.date_to

    fixed_asset_accs = Account.objects.filter(
        account_type = 'long term assets')
    current_asset_accs = Account.objects.filter(
        Q(account_type = 'current assets')| Q(code = '4460'))
    current_liability_accs = Account.objects.filter(
        account_type = 'current liabilities')
    capital_accs = Account.objects.filter(~Q(code = '3010'),
        account_type = 'equity')
    income_accs = Account.objects.filter(account_type = 'income')
    cost_of_sales_accs = Account.objects.filter(Q(account_type = 'cost of sales'),
        ~Q(code = '4460'))
    expense_accs = Account.objects.filter(account_type = 'expense')
    closing_stock_accs = Account.objects.filter(code = '4460')
    drawings_accs = Account.objects.filter(code = '3010')

    fixed_asset_amt = Decimal('0')
    current_asset_amt = Decimal('0')
    current_liability_amt = sum_account_balances(current_liability_accs,
        date_to = date_to, date_from = date_from)
    capital_amt = Decimal('0')

    income_amt = sum_account_balances(income_accs,
        date_from = date_from, date_to = date_to)
    cost_of_sales_amt = sum_account_balances(cost_of_sales_accs,
        date_from = date_from, date_to = date_to)
    expense_amt = sum_account_balances(expense_accs,
        date_from = date_from, date_to = date_to)
    closing_stock_amt = sum_account_balances(closing_stock_accs,
        date_from = date_from, date_to = date_to)
    drawings_amt = sum_account_balances(drawings_accs,
        date_from = date_from, date_to = date_to)
    net_profit_amt = income_amt - (cost_of_sales_amt - closing_stock_amt) - expense_amt

    #Fixed assets section
    table.append(['Fixed Assets', '', ''])
    for acc in fixed_asset_accs:
        amt = acc.balance_between(date__gte = date_from,
            date__lte = date_to)
        if amt > Decimal('0'):
            table.append([str(acc), '', amt])
            fixed_asset_amt += amt
    table.append(['', '', fixed_asset_amt])
    table.append(space)

    #Current assets section
    table.append(['Current Assets', '', ''])
    for acc in current_asset_accs:
        amt = acc.balance_between(date__gte = date_from,
            date__lte = date_to)
        if amt > Decimal('0'):
            table.append([str(acc), amt, ''])
            current_asset_amt += amt
    table.append(['', current_asset_amt, ''])
    table.append(['Less current liabilities', current_liability_amt, ''])
    assets_less_liabilities_amt = current_asset_amt-current_liability_amt
    table.append(['', '', assets_less_liabilities_amt])
    table.append(['', '', fixed_asset_amt + assets_less_liabilities_amt])
    table.append(space)

    #Capital Section
    table.append(['Capital', '', ''])
    for acc in capital_accs:
        amt = acc.balance_between(date__gte = date_from,
            date__lte = date_to)
        if amt > Decimal('0'):
            table.append([str(acc), '', amt])
            capital_amt += amt
    table.append(['Add Net Profit*', '', net_profit_amt])
    add_net_profit_amt = net_profit_amt + capital_amt
    table.append(['', '', add_net_profit_amt])
    table.append(['Less Drawings', '', drawings_amt])
    less_drawing_amt = add_net_profit_amt - drawings_amt
    table.append(['', '', less_drawing_amt])
    table.append(space)

    return table
    

def trial_balance_table_preset(virtual_journal):
    virtual_journal.col_headings = ['Details', 'Dr', 'Cr']
    table = []
    table.append(virtual_journal.col_headings)
    accounts = Account.objects.all()
    cr_tot = Decimal('0')
    db_tot = Decimal('0')
    for a in accounts:
        use_record = True
        record = [a.name]
        balance = a.debit_minus_credit_balance(
            date__gte = virtual_journal.rule.date_from,
            date__lte = virtual_journal.rule.date_to)


        if balance < 0:
            record += ['-', abs(balance)]
            cr_tot += abs(balance)
        elif balance > 0:
            record += [balance, '-']
            db_tot += abs(balance)
        else:
            use_record = False
            record += ['0.00', '0.00']

        if use_record:
            table.append(record)

    table.append(['', db_tot, cr_tot])
    return table