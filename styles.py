import copy
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image,ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

from django.conf import settings

# black = '#000000'
# dark_blue = '#01429a'
# grey = '#e8e8e8'
# red = '#c11e2e'

class OPEXATableStyle(TableStyle):

    def append_command(self, cmd):
        self._cmds.append(cmd)

class ColorSwatch():

    def __init__(self, **colors):
        for color, v in colors.items():
            setattr(self, color, v)


class PDFTableStyle():

    def __init__(self, name, style):
        self.name = name
        self.table_style = style

    def append_command(self, cmd):
        self.table_style.append_command(cmd)



def style_options():
    styles = getSampleStyleSheet()
    options = {'paragraph': {}}

    colors = {'black':'#000000', 'dark_blue':'#01429a', 'grey':'#e8e8e8',
        'red':'#c11e2e'}

    normalFontSize = 8
    subheadingFontSize = 13
    headingFontSize = 20
    options.update({'normalFontSize':normalFontSize,
        'subheadingFontSize':subheadingFontSize,
        'headingFontSize':headingFontSize,
        'color_swatch':ColorSwatch(**colors)})


    #Add T-Account style
    style_config = [
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('BACKGROUND', (2,0),(2,-1), colors['grey']),
        ('BACKGROUND', (-1,0),(-1,-1), colors['grey']),    

        ('FONTSIZE', (0, 0), (-1, -1), normalFontSize),

        ('LINEBELOW', (0, 0), (-1, 0), 1, colors['black']),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors['black']),
        ('LINEAFTER', (2, 0), (2, -1), 1, colors['black'])
    ]

    t_acc_option = PDFTableStyle('t_account',OPEXATableStyle(style_config))
    options.update({t_acc_option.name:t_acc_option})

    #Add Trial Balance style
    trial_bal_config = [
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),

        # Grid
        ('LINEAFTER', (0, 0), (-1, -1), 1, colors['black']),
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors['black']),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors['black']),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors['black']),

    ]

    trial_bal_option = PDFTableStyle('trial_balance',OPEXATableStyle(trial_bal_config))
    options.update({trial_bal_option.name:trial_bal_option})

    #Add Trial Balance style
    pl_option = [
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        # Grid
        ('LINEAFTER', (0, 0), (-1, -1), 1, colors['black']),
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors['black']),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors['black']),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors['black'])
    ]

    pl_option = PDFTableStyle('profit_and_loss',OPEXATableStyle(trial_bal_config))
    options.update({pl_option.name:pl_option})


    #Paragraph Styles
    sub_heading_style = ParagraphStyle('Sub-Heading')
    sub_heading_style.textColor = 'black'
    sub_heading_style.fontSize = subheadingFontSize
    sub_heading_style.alignment = TA_CENTER
    options['paragraph'].update({'sub_heading':sub_heading_style})

    heading_style = ParagraphStyle('Heading')
    heading_style.textColor = 'black'
    heading_style.fontSize = headingFontSize
    heading_style.alignment = TA_CENTER
    options['paragraph'].update({'heading':heading_style})


    default_style = copy.copy(styles["Normal"])
    options['paragraph'].update({'default':default_style})

    centered = copy.copy(styles["Normal"])
    centered.alignment = TA_CENTER
    options['paragraph'].update({'centered':centered})

    centered_sub_heading = copy.copy(centered)
    centered_sub_heading.fontSize = subheadingFontSize
    options['paragraph'].update({'centered_sub_heading':centered_sub_heading})

    return options

class StyleManager():

    def new_style():
        pass