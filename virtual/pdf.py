try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from os.path import expanduser
from importlib import import_module
import datetime
from decimal import Decimal

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image,ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import utils

from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models

heading_style = ParagraphStyle('Heading')
heading_style.textColor = 'black'
heading_style.fontSize = 25
heading_style.alignment = TA_CENTER

sub_heading_style = ParagraphStyle('Sub-Heading')
sub_heading_style.textColor = 'black'
sub_heading_style.fontSize = 13
sub_heading_style.alignment = TA_CENTER

class PDFBuilder():
    pdf_type = 'general_pdf'

    def __init__(self):
        self.file_buffer = StringIO()
        self.doc = SimpleDocTemplate(self.file_buffer,
            topMargin=10, bottomMargin=10)

        #The styles avilable for the PDF builder are defined in the settings.py, as the BOOKS_PDF_STYLES
        # setting. This represents a function we need to import and call in order to
        # get the styles that should be available to the PDFBuilder objects.

        module_path_split = settings.OPEXA_BOOKS_PDF_STYLES.split('.')
        module_path = ".".join(module_path_split[:-1])
        func = module_path_split[-1]
        styles_module = import_module(module_path)
        self.styles = getattr(styles_module, func)()

    def get_filename(self, file_name = None):
        if file_name:
            return file_name
        return '{}.pdf'.format(self.pdf_type)

    def build(self, elements, file_name = None):
        prebuild = getattr(self, 'build_instructions')(elements)
        self.doc.build(prebuild)
        pdf = self.file_buffer.getvalue()
        fp = expanduser('~/tmp/{}'.format(self.get_filename(file_name = file_name)))
        with open(fp, 'wb') as f:
            f.write(pdf)
        return ContentFile(pdf)

    def unpack_list_data(self, line):

        new_line = []
        for data_point in line:
            if isinstance(data_point, list):
                new_line.append(self.unpack_list_data(data_point))
            else:
                # print ('Cleaning: {}'.format(data_point))
                new_line.append(self.clean_data_point(data_point))
        return new_line

    def clean_data_point(self, data_point):

        if isinstance(data_point, datetime.date) or isinstance(data_point, datetime.datetime):
            return data_point.strftime(settings.BOOKS_SHORT_DATE_FORMAT)

        return str(data_point)

class BalanceSheetPDFBuilder(PDFBuilder):

    def build_instructions(self, bs_dict):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(bs_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2
        other_columns_width = (settings.OPEXA_BOOKS_PDF_PAGE_WIDTH - detail_colum_width)/2
        col_widths=[detail_colum_width, other_columns_width, other_columns_width]

        bs_table = []

        sub_section_ident = 8
        #Add section to calculate gross profit
        bs_table.append(['Assets', '', ''])
        for entry in bs_dict['assets_section']['entry_list']:
            bs_table.append([' '*sub_section_ident + str(entry[0]), '', entry[1]])
        bs_table.append(['', '', bs_dict['assets_section']['sum_tot']])
        asset_total_line = len(bs_table) - 1

        bs_table.append(['Liabilities', '', ''])
        for entry in bs_dict['liabilities_section']['entry_list']:
            bs_table.append([' '*sub_section_ident + str(entry[0]), '', entry[1]])
        bs_table.append(['', '', bs_dict['liabilities_section']['sum_tot']])
        liabilities_total_line = len(bs_table) - 1

        bs_table.append(['Capital', '', ''])
        for entry in bs_dict['capital_section']['entry_list']:
            bs_table.append([' '*sub_section_ident + str(entry[0]), '', entry[1]])
        bs_table.append(['', '', bs_dict['capital_section']['sum_tot']])
        capital_total_line = len(bs_table) - 1

        t=Table(bs_table,colWidths=col_widths)
        elements.append(t)
        elements.append(Spacer(1,5))
        return elements

class ProfitAndLossPDFBuilder(PDFBuilder):

    pdf_type = 'profit_and_loss'

    def build_instructions(self, pl_dict):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(pl_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2
        other_columns_width = (settings.OPEXA_BOOKS_PDF_PAGE_WIDTH - detail_colum_width)/2
        col_widths=[detail_colum_width, other_columns_width, other_columns_width]

        pl_table = []

        sub_section_ident = 8
        #Add section to calculate gross profit
        pl_table.append(['Sales', '', pl_dict['income_section']['sum_tot']])

        pl_table.append(['Less production cost of goods sold:', '', ''])
        for cost_entry in pl_dict['cost_of_production_section']['entry_list']:
            pl_table.append([' '*sub_section_ident + str(cost_entry[0]), cost_entry[1], ''])
        pl_table.append(['', '', '({})'.format(pl_dict['cost_of_production_section']['sum_tot'])])
        pl_table.append(['Gross Profit', '', pl_dict['gross_profit']])
        gross_profit_line_index = len(pl_table) - 1

        #Add section to calculate Net Profit
        pl_table.append(['Less expenses:', '', ''])
        for cost_entry in pl_dict['expenses_section']['entry_list']:
            pl_table.append([' '*sub_section_ident + str(cost_entry[0]), cost_entry[1], ''])
        pl_table.append(['', '', '({})'.format(pl_dict['expenses_section']['sum_tot'])])
        pl_table.append(['Net Profit', '', pl_dict['net_profit']])
        net_profit_line_index = len(pl_table) - 1

        t=Table(pl_table,colWidths=col_widths)
        elements.append(t)
        elements.append(Spacer(1,5))

        #Update the default style to underline the totals in the document
        basic_pl_style = self.styles['profit_and_loss'].table_style
        basic_pl_style.append_command(
            ('FONTSIZE', (0, gross_profit_line_index), (-1, gross_profit_line_index), self.styles['subheadingFontSize']))
        basic_pl_style.append_command(
            ('LINEABOVE', (-1, gross_profit_line_index), (-1, gross_profit_line_index), 0.3, self.styles['color_swatch'].black))
        basic_pl_style.append_command(
            ('LINEBELOW', (-1, gross_profit_line_index), (-1, gross_profit_line_index), 0.3, self.styles['color_swatch'].black))
        basic_pl_style.append_command(
            ('TEXTCOLOR', (0, gross_profit_line_index-1), (-1, gross_profit_line_index-1), self.styles['color_swatch'].red))
        basic_pl_style.append_command(
            ('FONTSIZE', (0, net_profit_line_index), (-1, net_profit_line_index), self.styles['subheadingFontSize']))
        basic_pl_style.append_command(
            ('TEXTCOLOR', (0, net_profit_line_index-1), (-1, net_profit_line_index-1), self.styles['color_swatch'].red))
        basic_pl_style.append_command(
            ('LINEABOVE', (-1, net_profit_line_index), (-1, net_profit_line_index), 0.3, self.styles['color_swatch'].black))
        t.setStyle(basic_pl_style)
        return elements

class TrialBalancePDFBuilder(PDFBuilder):

    pdf_type = 'trial_balance'

    def build_instructions(self, tb_dict):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(tb_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2
        other_columns_width = (settings.OPEXA_BOOKS_PDF_PAGE_WIDTH - detail_colum_width)/2
        col_widths=[detail_colum_width, other_columns_width, other_columns_width]

        debit_credit_table = [
            ['', Paragraph('Debit',self.styles['paragraph']['centered_sub_heading']),
            Paragraph('Credit',self.styles['paragraph']['centered_sub_heading'])]
        ]
        t=Table(debit_credit_table,colWidths=col_widths)
        elements.append(t)
        elements.append(Spacer(1,5))

        tb_entries = tb_dict['entries']
        tb_entries.append(['', '', ''])
        tb_entries.append(['', tb_dict['debit_total'], tb_dict['credit_total']])
        t=Table(self.unpack_list_data(tb_entries), colWidths = col_widths)
        t.setStyle(self.styles['trial_balance'].table_style)
        elements.append(t)


        return elements


class TAccountPDFBuilder(PDFBuilder):
    pdf_type = 't_account'

    def build_instructions(self, elements):
        #Replace heading text with formatted Paragraph object
        new_heading = Paragraph(elements[0][0],
            self.styles['paragraph']['heading'])

        #First section, the account heading, a space and then the headings for the debit and
        #credit sides of the account
        pre_built_elements = [new_heading]
        pre_built_elements.append(Spacer(1,25))

        debit_credit_table = [[Paragraph('Debit',
                        self.styles['paragraph']['sub_heading']),
                    Paragraph('Credit',
                        self.styles['paragraph']['sub_heading'])]]
        t=Table(debit_credit_table,colWidths=[settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2, settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2])
        pre_built_elements.append(t)
        pre_built_elements.append(Spacer(1,5))

        #Take out the section representing all of the single entry details and convert
        # them into a table
        table_data = elements[1:]
        unpacked_table_data = self.unpack_list_data(table_data)

        half_page_width = settings.OPEXA_BOOKS_PDF_PAGE_WIDTH/2
        date_column_width = 60
        value_column_width = 80
        other_columns_width = (half_page_width - date_column_width - value_column_width)
        col_widths = [date_column_width, other_columns_width, value_column_width, date_column_width,
            other_columns_width, value_column_width]
        t=Table(unpacked_table_data, colWidths=col_widths)
        t.setStyle(self.styles['t_account'].table_style)

        #Insert the new table back in the elements list
        pre_built_elements.append(t)
        return pre_built_elements



def pdf_from_preset(virtual_joural):
    if virtual_joural.rule.preset == 'TB':
        return trial_balance_preset(virtual_joural)


def trial_balance_preset(virtual_joural):
    file_buffer = StringIO()
    doc = SimpleDocTemplate(file_buffer, topMargin=10,bottomMargin=10)
    styles=getSampleStyleSheet()
    elements = []

    col_widths = [350, 100, 100]

    elements.append(
        Paragraph(virtual_joural.rule.name,
            heading_style))
    elements.append(Spacer(1, 15))

    sub_heading = 'Period Between {0} and {1}'.format(
        virtual_joural.rule.after_date,
        virtual_joural.rule.before_date)

    elements.append(
        Paragraph(sub_heading,
            sub_heading_style))
    elements.append(Spacer(1, 30))


    style_data = [
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        ('BACKGROUND', (1,0),(-1,-1), '#a1aec3'),
        ('LINEBELOW', (-1, -1), (-1, -1), 0.5, colors.black), 
        # ('VALIGN',(1,-1),(0,-1),'MIDDLE'),
        ('LINEBELOW', (-2, -1), (-1, -1), 1, colors.blue),
        ('LINEABOVE', (-2, -1), (-1, -1), 0.7, colors.blue),    

        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),


        ('LINEBEFORE', (1, 0), (-1, -1), 0.2, colors.black),
        ('LINEAFTER', (1, 0), (-1, -1), 0.2, colors.black),
        ]

    default_style = TableStyle(style_data)
    t=Table(virtual_joural.table,
        colWidths=col_widths
        )
    t.setStyle(default_style)
    elements.append(t)
    doc.build(elements)
    pdf = file_buffer.getvalue()
    with open('/tmp/virtual_joural.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf)

def journal_to_pdf(virtual_joural):
    file_buffer = StringIO()
    doc = SimpleDocTemplate(file_buffer, topMargin=10,bottomMargin=10)
    styles=getSampleStyleSheet()
    elements = []

    col_widths = [35,70]
    remaining_width = (550-200)/2
    extra_cols = len(virtual_joural.col_headings[2:])
    for i in range(extra_cols):
        col_widths.append(remaining_width/extra_cols)
    col_widths = col_widths + col_widths

    elements.append(
        Paragraph(virtual_joural.rule.name,
            heading_style))
    elements.append(Spacer(1, 30))


    style_data = [
        ('LINEBELOW',(0,0),(-1,0),1,colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 5),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,0),'MIDDLE'),
        ('BACKGROUND', (0,0),(-1,0), '#a1aec3'), 
        ('LINEBEFORE', (0, 0), (-1, -1), 0.2, colors.blue),   

        ('FONTSIZE', (0, 0), (-1, -1), 6),  
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN',(0, 1), (-1, -1),'MIDDLE'),
        ]
    middel_index = int(len(col_widths)/2)
    style_data.append(
        ('LINEBEFORE', (middel_index, 1), (middel_index, -1), 1, colors.black)
    )

    default_style = TableStyle(style_data)

    t=Table(virtual_joural.table,
        colWidths=col_widths
        )
    t.setStyle(default_style)
    elements.append(t)
    doc.build(elements)
    pdf = file_buffer.getvalue()
    with open('/tmp/virtual_joural.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf)