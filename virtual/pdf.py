try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

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

from books.conf.settings import PDF_PAGE_WIDTH




heading_style = ParagraphStyle('Heading')
heading_style.textColor = 'black'
heading_style.fontSize = 25
heading_style.alignment = TA_CENTER

sub_heading_style = ParagraphStyle('Sub-Heading')
sub_heading_style.textColor = 'black'
sub_heading_style.fontSize = 13
sub_heading_style.alignment = TA_CENTER

class PDFBuilder():

    def __init__(self):
        self.file_buffer = StringIO()
        self.doc = SimpleDocTemplate(self.file_buffer,
            topMargin=10, bottomMargin=10)

        #The styles avilable for the PDF builder are defined in the settings.py, as the BOOKS_PDF_STYLES
        # setting. This represents a function we need to import and call in order to
        # get the styles that should be available to the PDFBuilder objects.
        module_path_split = settings.BOOKS_PDF_STYLES.split('.')
        module_path = ".".join(module_path_split[:-1])
        func = module_path_split[-1]
        styles_module = import_module(module_path)
        self.styles = getattr(styles_module, func)()

    def build(self, style, elements):
        prebuild = getattr(self, '_prebuild_' + style)(elements)
        self.doc.build(prebuild)
        pdf = self.file_buffer.getvalue()
        with open('/tmp/{}.pdf'.format(style), 'wb') as f:
            f.write(pdf)
        return ContentFile(pdf)

    def unpack_list_data(self, line):
        new_line = []
        for data_point in line:
            if isinstance(data_point, list):
                new_line.append(self.unpack_list_data(data_point))
            else:
                new_line.append(self.clean_data_point(data_point))
        return new_line

    def clean_data_point(self, data_point):

        if isinstance(data_point, datetime.date):
            return Paragraph(data_point.strftime(settings.BOOKS_SHORT_DATE_FORMAT),
                self.styles['paragraph']['default'])

        if isinstance(data_point, Decimal):
            return Paragraph(str(data_point),
                self.styles['paragraph']['default'])

        if isinstance(data_point, str):
            return Paragraph(data_point,
                self.styles['paragraph']['default'])
        return data_point



    def _prebuild_t_account(self, elements):
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
        t=Table(debit_credit_table,colWidths=[PDF_PAGE_WIDTH/2, PDF_PAGE_WIDTH/2])
        pre_built_elements.append(t)
        pre_built_elements.append(Spacer(1,5))

        #Take out the section representing all of the single entry details and convert
        # them into a table
        table_data = elements[1:]
        unpacked_table_data = self.unpack_list_data(table_data)

        half_page_width = PDF_PAGE_WIDTH/2
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