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

from django.core.files.base import ContentFile

heading_style = ParagraphStyle('Table Heading')
heading_style.textColor = 'black'
heading_style.fontSize = 25
heading_style.alignment = TA_CENTER

def journal_to_pdf(virtual_joural):
    file_buffer = StringIO()
    doc = SimpleDocTemplate(file_buffer, topMargin=10,bottomMargin=10)
    styles=getSampleStyleSheet()
    elements = []

    col_widths = [50,50]
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
        ('LINEBEFORE', (middel_index, 0), (middel_index, -1), 1, colors.black)
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