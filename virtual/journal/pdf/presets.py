try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image,ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import utils
from reportlab.lib.pagesizes import landscape, letter

from django.core.files.base import ContentFile

heading_style = ParagraphStyle('Heading')
heading_style.textColor = 'black'
heading_style.fontSize = 25
heading_style.alignment = TA_CENTER

sub_heading_style = ParagraphStyle('Sub-Heading')
sub_heading_style.textColor = 'black'
sub_heading_style.fontSize = 13
sub_heading_style.alignment = TA_CENTER

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
        virtual_joural.rule.date_from,
        virtual_joural.rule.date_to)

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
    with open('/tmp/trial_balance_journal.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf), 'trial_balance_journal.pdf'

def balace_sheet_preset(virtual_joural):
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
        virtual_joural.rule.date_from,
        virtual_joural.rule.date_to)

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
    # t.setStyle(default_style)
    elements.append(t)
    doc.build(elements)
    pdf = file_buffer.getvalue()
    with open('/tmp/balance_sheet_journal.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf), 'balance_sheet_journal.pdf'

def profit_and_loss_preset(virtual_joural):
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
        virtual_joural.rule.date_from,
        virtual_joural.rule.date_to)

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
    # t.setStyle(default_style)
    elements.append(t)
    doc.build(elements)
    pdf = file_buffer.getvalue()
    with open('/tmp/profit_and_loss_account.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf), 'profit_and_loss_account.pdf'

def cash_book_preset(virtual_joural):
    file_buffer = StringIO()
    doc = SimpleDocTemplate(file_buffer, topMargin=10,bottomMargin=10,
        pagesize=landscape(letter))
    styles=getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 7
    elements = []

    formatted_table = []
    for row in virtual_joural.table:
        formatted_row = []
        for entry in row:
            try:
                formatted_row.append(Paragraph(entry, styleBH))
            except AttributeError:
                formatted_row.append(entry)
        formatted_table.append(formatted_row)


    #Dynamically determine the width 
    col_widths = [35,100]
    remaining_width = (780-270)/2
    extra_cols = int((len(virtual_joural.table[0])/2)-2)
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

    t=Table(formatted_table,
        colWidths=col_widths
        )
    t.setStyle(default_style)
    elements.append(t)
    doc.build(elements)
    pdf = file_buffer.getvalue()
    with open('/tmp/cash_book_joural.pdf', 'wb') as f:
        f.write(pdf)
    return ContentFile(pdf), 'cash_book_joural.pdf'