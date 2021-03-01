try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from importlib import import_module
import datetime
from decimal import Decimal
from pathlib import Path
import copy

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image,ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
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
    page_size = A4
    sample_style_sheet = getSampleStyleSheet()

    def __init__(self, font_name = 'Roboto'):
        self.file_buffer = StringIO()
        self.doc = SimpleDocTemplate(self.file_buffer,
            topMargin=10, bottomMargin=10,
            rightMargin = 10, leftMargin = 10, 
            pagesize = self.page_size)

        self.font_name = font_name
        self.__set_styles()

    def create_style(self, **style_options):
        default_options = {'fontName':self.font_name}
        for option_name, value in default_options.items():
            if option_name not in style_options:
                style_options[option_name] = value

        style_sheet = copy.copy(self.sample_style_sheet['Normal'])
        for option_name, value in style_options.items():
            setattr(style_sheet, option_name, value)
        return style_sheet

    
    def Paragraph(self, content, **style_options):
        style = self.create_style(**style_options)
        return Paragraph(content, style)

    @property
    def page_width(self):
        return self.page_size[0]

    @property
    def page_height(self):
        return self.page_size[1]

    def get_filename(self, file_name = None):
        if file_name:
            return file_name
        return '{}.pdf'.format(self.pdf_type)

    def build(self, elements, file_name = None, write_to_file = False,
        **kwargs):
        prebuild = getattr(self, 'build_instructions')(elements, **kwargs)
        self.doc.build(prebuild)
        pdf = self.file_buffer.getvalue()

        if write_to_file:
            self.write_to_file(file_name, pdf)

        return ContentFile(pdf)

    def write_to_file(self, file_name, contents):
        """ Write document to file. """

        out_path = Path(settings.BASE_DIR).joinpath('tmp',
            self.get_filename(file_name = file_name))
        out_path.write_bytes(contents)

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
        """ Convert data into a string to make them compatible with being added to 
        a story. """
        if isinstance(data_point, datetime.date) or isinstance(data_point, datetime.datetime):
            return data_point.strftime(settings.BOOKS_SHORT_DATE_FORMAT)
        return str(data_point)

    @property
    def _base_table_style(self):
        style =  TableStyle([])
        style.add('FONT', (0,0), (-1,-1), self.font_name)
        return style

    def __set_styles(self):
        """ Retrieves the user-defined set of styles that are avaiable. """

        module_path_split = settings.BOOKS_PDF_STYLES.split('.')
        module_path = ".".join(module_path_split[:-1])
        func = module_path_split[-1]
        styles_module = import_module(module_path)
        self.styles = getattr(styles_module, func)()

class BalanceSheetPDFBuilder(PDFBuilder):

    def build_instructions(self, bs_dict, **kwargs):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(bs_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = self.page_width/2
        other_columns_width = (self.page_width - detail_colum_width)/2
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

    def build_instructions(self, pl_dict, **kwargs):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(pl_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = self.page_width/2
        other_columns_width = (self.page_width - detail_colum_width)/2
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

    def build_instructions(self, tb_dict, **kwargs):
        #Trial balances supply their build elements as a Dict object
        elements = [] 

        #Add heading
        elements.append(Paragraph(tb_dict['heading'],
            self.styles['paragraph']['heading']))
        elements.append(Spacer(1,25))

        #Work out column widths
        detail_colum_width = self.page_width/2
        other_columns_width = (self.page_width - detail_colum_width)/2
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

    def build_instructions(self, elements, **kwargs):
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
        t=Table(debit_credit_table,colWidths=[self.page_width/2, self.page_width/2])
        pre_built_elements.append(t)
        pre_built_elements.append(Spacer(1,5))

        #Take out the section representing all of the single entry details and convert
        # them into a table
        table_data = elements[1:]
        unpacked_table_data = self.unpack_list_data(table_data)

        half_page_width = self.page_width/2
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

class InvoiceBuilder(PDFBuilder):
    pdf_type = 'invoice'
    page_size = A5

    def build_instructions(self, elements = [], invoice_num = 0, invoice_entries = [],
        date = None, due = None,  **kwargs):

        # Heading
        elements.append(self.Paragraph('Invoice', fontName = 'RobotoBI', fontSize = 25,
            alignment = TA_CENTER))
        elements.append(Spacer(1,45))

        # Spacing to make subsequent tables line up
        page_width = self.page_width
        col_widths = [page_width/3, page_width/4*(1/3),page_width/4*(2/3),page_width/4]

        # Invoice details (No, date, due)
        invoice_details_table = []
        
        extra_zeros = 6-invoice_num
        if extra_zeros > 0:
            invoice_num = '0'*extra_zeros + str(invoice_num)

        if settings.BOOKS_LOGO_SMALL:
            logo =  Image(settings.BOOKS_LOGO_SMALL, width=40, height=50)
            logo.hAlign = 'CENTER'
        else:
            logo = ''

        invoice_details_table.append([logo,'', 'No:', invoice_num])
        invoice_details_table.append(['','', 'Date:', date.strftime("%d-%m-%y")])
        invoice_details_table.append(['','', 'Due:', due.strftime("%d-%m-%y")])
        t=Table(invoice_details_table, colWidths = col_widths)
        t.setStyle(self._invoice_details_table_style)
        elements.append(t)
        elements.append(Spacer(1,30))

        # Invoice entries (Description, QTY, Unit Price, Total)
        balance_due = 0
        invoice_entries_table = []
        paragraph_kwargs = {'alignment':TA_CENTER}
        invoice_entries_table.append(['Description', 'QTY', 'Unit Price', 'Total'])
        entries_present = 0
        for e in invoice_entries:
            invoice_entries_table.append([self.Paragraph(e['description']),
                e['quantity'], f"{e['unit_price']:.2f}", f"{e['total']:.2f}"])
            balance_due += e['total']
            entries_present += 1

        # Add blank spaces to the invoice, if any are required
        blank_spaces = 3-entries_present
        if blank_spaces > 0:
            for i in range(blank_spaces):
                invoice_entries_table.append(['','','',''])

        t=Table(invoice_entries_table, colWidths = col_widths)
        t.setStyle(self._entries_table_style)
        elements.append(t)
        elements.append(Spacer(1,15))

        # Balance due line
        balance_due_table = [[' ', ' ', 'Amt Due', f'$ {balance_due:.2f}']]
        t=Table(balance_due_table, colWidths = col_widths)
        t.setStyle(self._totals_table_style)
        elements.append(t)
        elements.append(Spacer(1,45))

        thank_you = self.Paragraph('Thank-you for you business!', alignment = TA_CENTER)
        elements.append(thank_you)
        elements.append(Spacer(1,35))

        elements.append(self.Paragraph('Contact Us:',
            alignment = TA_CENTER, fontSize = 11, fontName = 'RobotoB'))
        elements.append(Spacer(1,7))
        elements.append(self.Paragraph("Tatenda Tambo",
            alignment = TA_CENTER))
        elements.append(self.Paragraph("Cell: +263 782 201 884",
            alignment = TA_CENTER))
        elements.append(self.Paragraph("E-mail: tatendatambo@gmail.com",
            alignment = TA_CENTER))
        return elements

    @property
    def _paragraph_style(self):
        return self.__paragraph_style
    

    @property
    def _entries_table_style(self):
        style =  self._base_table_style
        style.add('FONT',(0,0),(-1,0), 'RobotoB')
        style.add('BOX',(0,0),(-1,0),0.5,"#999999")
        style.add('ALIGN',(0,0),(-1,0), "CENTER")
        style.add('ALIGN',(1,1),(2,-1), "CENTER")
        style.add('ALIGN',(2,1),(-1,-1), "RIGHT")
        style.add('VALIGN',(0,0),(-1,-1), "TOP")
        style.add('GRID',(0,1),(-1,-1),0.5,"#999999")
        style.add('ROWBACKGROUNDS', (0,0), (-1,-1), ["#ffffff", "#f3f3f3"])
        return style

    @property
    def _invoice_details_table_style(self):
        style =  self._base_table_style
        style.add('ALIGN', (2,0), (2,-1),'RIGHT')
        style.add('ALIGN', (0,0), (1,-1),'LEFT')
        style.add('ALIGN', (-1,0), (-1,-1),'RIGHT')
        style.add('LINEBELOW', (-1,0), (-1,-1), 0.25, '#f3f3f3')
        style.add('SPAN', (0,0), (1,-1))
        return style

    @property
    def _totals_table_style(self):
        style =  self._base_table_style
        style.add('ALIGN', (2,0), (2,-1),'CENTER')
        style.add('ALIGN', (-1,0), (-1,-1),'RIGHT')
        style.add('TEXTCOLOR', (2,0), (-1,-1),"#1f3864")
        style.add('FONT',(1,0),(-1,1), 'RobotoB')
        style.add('FONTSIZE',(1,0),(-1,1), 11)
        style.add('LINEABOVE',(2,0),(-1,1),0.25, "#000000")
        style.add('LINEBELOW',(2,0),(-1,1),0.25, "#000000")
        return style
    


    
    
### TODO: This should be removed, since the journals and everything else wont
### really be necessary going forward
def pdf_from_preset(virtual_joural):
    if virtual_joural.rule.preset == 'TB':
        return trial_balance_preset(virtual_joural)


def trial_balance_preset(virtual_joural):
    file_buffer = StringIO()
    doc = SimpleDocTemplate(file_buffer, topMargin=10, bottomMargin=10)
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