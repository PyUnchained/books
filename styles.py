black = '#000000'
dark_blue = '#01429a'

def style_options():
    options = {}

    #Add T-Account style
    t_acc_option = {'t_account':
        [
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        ('BACKGROUND', (1,0),(-1,-1), '#a1aec3'),
        ('LINEBELOW', (-1, -1), (-1, -1), 0.5, black), 
        # ('VALIGN',(1,-1),(0,-1),'MIDDLE'),
        ('LINEBELOW', (-2, -1), (-1, -1), 1, dark_blue),
        ('LINEABOVE', (-2, -1), (-1, -1), 0.7, dark_blue),    

        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 1, black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, black),

        ('LINEBEFORE', (1, 0), (-1, -1), 0.2, black),
        ('LINEAFTER', (1, 0), (-1, -1), 0.2, black),
        ]}

    options.update(t_acc_option)
    return options