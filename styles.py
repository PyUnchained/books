from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image,ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

from books.conf.settings import PDF_PAGE_WIDTH

black = '#000000'
dark_blue = '#01429a'
grey = '#e8e8e8'

class PDFTableStyle():

    def __init__(self, name, style):
        self.name = name
        self.table_style = style

def style_options():
    styles = getSampleStyleSheet()
    options = {'paragraph': {}}

    normalFontSize = 8

    #Add T-Account style
    style_config = [
        # ('ALIGN',(2,0),(2,-1),'CENTER'),
        # ('ALIGN',(-1,0),(-1,-1),'CENTER'),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('BACKGROUND', (2,0),(2,-1), grey),
        ('BACKGROUND', (-1,0),(-1,-1), grey),    

        ('FONTSIZE', (0, 0), (-1, -1), normalFontSize),

        ('LINEBELOW', (0, 0), (-1, 0), 1, black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, black),
        ('LINEAFTER', (2, 0), (2, -1), 1, black)]

    t_acc_option = PDFTableStyle('t_account',TableStyle(style_config))
    options.update({t_acc_option.name:t_acc_option})


    #Paragraph Styles
    sub_heading_style = ParagraphStyle('Sub-Heading')
    sub_heading_style.textColor = 'black'
    sub_heading_style.fontSize = 13
    sub_heading_style.alignment = TA_CENTER
    options['paragraph'].update({'sub_heading':sub_heading_style})

    heading_style = ParagraphStyle('Heading')
    heading_style.textColor = 'black'
    heading_style.fontSize = 25
    heading_style.alignment = TA_CENTER
    options['paragraph'].update({'heading':heading_style})


    default_style = styles["Normal"]
    options['paragraph'].update({'default':default_style})

    return options