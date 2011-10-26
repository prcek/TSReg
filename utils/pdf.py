
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs/reportlab.zip')
#sys.path.insert(0, 'libs')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,A6,landscape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch,mm,cm
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,PageBreak

import os
import re
import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'

pdfmetrics.registerFont(TTFont('DejaVuSansMono', os.path.join(folderFonts,'DejaVuSansMono.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(folderFonts,'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', os.path.join(folderFonts,'DejaVuSansBold.ttf')))


TEST_TEXT = "Příliš žluťoučký kůň úpěl ďábelské ódy"

import logging
import StringIO
import datetime

from utils.locale import local_timezone

#from pytz.gae import pytz

from xml.sax.saxutils import escape

def getNow():
#    tz = pytz.timezone('Europe/Prague') 
    now = datetime.datetime.utcnow() 
    local_now = local_timezone.fromutc(now)

    return local_now.strftime("%Y-%m-%d %H:%M:%S")


def nonone(s):
    if s is None:
        return ""
    return s



def getStyleSheet():
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName='DejaVuSansMono',
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='Heading',
                                  parent=stylesheet['Normal'],
                                  fontName = 'DejaVuSansBold',
                                  fontSize=18,
                                  leading=22,
                                  spaceAfter=6),
                   )
 
    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = 'DejaVuSansBold',
                                  fontSize=18,
                                  leading=22,
                                  alignment=TA_CENTER,
                                  spaceAfter=6),
                   )
    stylesheet.add(ParagraphStyle(name='Post',
                                  fontName='DejaVuSansMono',
                                  fontSize=9)
                   )

    stylesheet.add(ParagraphStyle(name='Card',
                                  fontName='DejaVuSansBold',
                                  fontSize=9)
                   )

    stylesheet.add(ParagraphStyle(name='CardHeaderLeft', parent=stylesheet['Card'],
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
                                  )
                   )

    stylesheet.add(ParagraphStyle(name='CardHeaderRight', parent=stylesheet['Card'],
                                  textColor=colors.black,
                                  alignment=TA_CENTER,
                                    leading=8,
                                    fontSize=8,
                                  )
                   )

    stylesheet.add(ParagraphStyle(name='CardSeason', parent=stylesheet['Card'],
                                  textColor=colors.black,
                                  alignment=TA_CENTER,
                                  fontSize=8,
                                  )
                   )

    stylesheet.add(ParagraphStyle(name='CardName', parent=stylesheet['Card'],
                                  fontSize=10,
                                  textColor=colors.black,
                                  alignment=TA_LEFT,
                                  )
                   )

    stylesheet.add(ParagraphStyle(name='CardSurname', parent=stylesheet['Card'],
                                  fontSize=13,
                                  textColor=colors.black,
                                  alignment=TA_RIGHT,
                                  )
                   )


    stylesheet.add(ParagraphStyle(name='CardCode', parent=stylesheet['Card'],
                                  textColor=colors.black,
                                  alignment=TA_CENTER,
                                  leading=16,
                                  fontSize=18,
                                  )
                   )

    stylesheet.add(ParagraphStyle(name='CardInfoLines', parent=stylesheet['Card'],
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
                                  )
                   )




    return stylesheet


def students_table(output,course,students):

#    if course.group_mode == 'School':
    ps = landscape(A4)
#    else:
#        ps = A4
    
    doc = SimpleDocTemplate(output, pagesize=ps) 

    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']


    elements = []

    elements.append(Paragraph(u"Kurz %s - %s - %s (%s)"%(escape(course.code),escape(course.name), escape(course.folder_name()),escape(course.season_name())),styleH))
    elements.append(Paragraph(u"ke dni %s"%getNow(),styleN))


    if course.group_mode == 'School':
        widths = [ 0.8*cm, 0.8*cm, 3*cm, 4*cm, 3*cm, 1.1*cm, 1.1*cm, 3*cm,5*cm,1.2*cm,4.0*cm ]
        data = [ ['č.','t.č','kód','přijmení','jméno','platba','dopl.', 'sleva', 'škola', 'třída', 'poznámka'] ]
    elif course.group_mode == 'Pair':
        widths = [ 0.8*cm, 0.8*cm, 3*cm, 4*cm, 3*cm, 1.1*cm, 1.1*cm, 3*cm, 0.5*cm,0.5*cm, 4.5*cm]
        data = [ ['č.','p.č','kód','přijmení','jméno', 'platba','dopl.', 'sleva', 'st.', 'ov.',  'poznámka'] ]
    else:
        widths = [ 0.8*cm, 3*cm, 4*cm, 3*cm, 1.1*cm, 1.1*cm, 3*cm, 0.5*cm,0.5*cm, 4.5*cm]
        data = [ ['č.','kód','přijmení','jméno', 'platba','dopl.', 'sleva', 'st.', 'ov.',  'poznámka'] ]
    i=1;
    for s in students:
        if s.x_pair_empty_slot:
            data.append([i,'---','---'])    
        else:
            if course.group_mode == 'School':
                data.append([s.x_no,s.x_class_no,s.ref_key,s.surname,s.name,s.to_pay,s.balance_due,s.discount,s.school,s.school_class, s.comment])
            else:
                if s.student:
                    st = 'A'
                else:   
                    st = 'N'
                if s.student_check:
                    stc = 'Ov'
                else:
                    stc = ''
                if course.group_mode == 'Pair':
                    data.append([s.x_no,s.x_pair_no,s.ref_key,s.surname,s.name,s.to_pay,s.balance_due,s.discount,st,stc,s.comment])
                else:
                    data.append([i,s.ref_key,s.surname,s.name,s.to_pay,s.balance_due,s.discount,st,stc,s.comment])
        i+=1
   # logging.info(data) 

    #TODO: add spare students
    pad = 1
    t=Table(data,colWidths=widths)
    t.setStyle(TableStyle([
#        ('BACKGROUND',(1,1),(-2,-2),colors.green),
#        ('TEXTCOLOR',(0,0),(1,-1),colors.red),
        ('GRID',(0,1),(-1,-1),0.3, colors.gray),
        ('FONT', (0,0), (-1,1), 'DejaVuSansBold'),
        ('FONT', (0,1), (-1,-1), 'DejaVuSansMono'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('LEFTPADDING',(0,0),(-1,-1),pad),
        ('RIGHTPADDING',(0,0),(-1,-1),pad),
        ('TOPPADDING',(0,0),(-1,-1),pad),
        ('BOTTOMPADDING',(0,0),(-1,-1),pad),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
 

    ]))
 
    elements.append(t)
    doc.build(elements)


def students_enroll(output,students):
    doc = SimpleDocTemplate(output, pagesize=landscape(A6) ,leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm, showBoundary=0)
    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']

    elements = []
    
    for s in students:
        rd = s.reg_datetime
        if rd is None:
            rd = '?'
        else:
            rd = rd.strftime("%Y-%m-%d")

        elements.append(Paragraph(u"Přihláška %s"%(escape(s.ref_key)),styleT))
        elements.append(Paragraph(u"dne %s, kurz %s %s"%(escape(rd),escape(s.course_code()),escape(s.course_season())),styleT))
        if s.student:
            stu = 'Ano'
        else:
            stu = 'Ne'
        data = [
            ["oslovení",s.addressing_loc()],
            ["jméno",nonone(s.name)],
            ["přijmení",nonone(s.surname)],
            ["cena",nonone(s.to_pay)],
            ["student",stu],
            ["e-mail",nonone(s.email)],
            ["telefon",nonone(s.phone)],
            ["adresa","%s %s"%(nonone(s.street),nonone(s.street_no))],
            ["","%s %s"%(nonone(s.post_code),nonone(s.city))],
        ]

        if nonone(s.school) != '' or nonone(s.school_class)!= '':
            data.append(['škola',"%s, %s"%(s.school,s.school_class)])

        if (not s.partner_ref_code is None) and s.partner_ref_code != '':
            data.append(['partner',s.partner_ref_code])
    
        if (not s.comment is None) and (s.comment != ''):
            data.append(['poznámka',s.comment])


        ipad=1
        t = Table(data, colWidths=[3*cm,9*cm],
        style=[
            ('GRID',(0,0),(-1,-1),0.5, colors.gray),
            ('FONT', (1,0), (1,-1), 'DejaVuSansBold'),
            ('FONT', (0,0), (0,-1), 'DejaVuSansMono'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
            ('TOPPADDING',(0,0),(-1,-1),ipad),
            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
 
        ])
        elements.append(t)
        elements.append(PageBreak())
                

    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
    doc.build(elements)




def students_card(output,cards):
    ipad = 1
    pad = 10


    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=1*cm, rightMargin=1*cm, topMargin=0.8*cm, bottomMargin=1*cm, showBoundary=0)
    styles = getStyleSheet()

    styleN = styles['Normal']
    styleHeaderLeft = styles['CardHeaderLeft']
    styleHeaderRight = styles['CardHeaderRight']
    styleIL  = styles['CardInfoLines']
    styleSeason  = styles['CardSeason']
    styleCode = styles['CardCode']
    styleName = styles['CardName']
    styleSurname = styles['CardSurname']



    elements = []

    cardcells = []
    for c in cards:

        info_empty = (c.info_line_1 is None or c.info_line_1=='') and (c.info_line_2 is None or c.info_line_2=='')
        
            
        c00 = Paragraph("<font size=12>STARLET</font><br/><font size=8>TANEČNÍ ŠKOLA<br/>MANŽELŮ BURYANOVÝCH</font>",styleHeaderLeft)
        c01 = Paragraph("ČÍSLO<br/>KURZU",styleHeaderRight)

        c10_n = Paragraph(escape(nonone(c.name)),styleName)
        c10_s = Paragraph(escape(nonone(c.surname)),styleSurname)


        code = nonone(c.course_code)
        if len(code)<=3:
            code_p = escape(code) 
        else:
            m = re.match('([^\d]*)(.*)',code)
            if m:
                code_p = "%s<br/>%s"%(escape(m.group(1)), escape(m.group(2)))
            else:       
                code_p = escape(code)

        c11 = Paragraph(code_p,styleCode)

        if info_empty:
            c20_bg = colors.white
        else:
            c20_bg = colors.black

        info_text = u""
        if not (c.info_line_1 is None or c.info_line_1==''):            
            info_text = info_text+escape(c.info_line_1)

        if not (c.info_line_2 is None or c.info_line_2==''):            
            if info_text != "":
                info_text = info_text + "<br/>"
            info_text = info_text + escape(c.info_line_2)
            

        c10 = Table([[c10_n],[c10_s]], style=[
       #     ('GRID',(0,0),(-1,-1),1, colors.black)
        ])
        
        c20 = Paragraph(str(info_text),styleIL)
        c21 = Paragraph(nonone(c.season_name),styleSeason)

        cc = Table([ [c00,c01],[c10,c11],[c20,c21] ], colWidths=[5.9*cm,1.5*cm],rowHeights=[1.50*cm,1.95*cm,0.95*cm], style=[
            ('GRID',(0,0),(-1,-1),1, colors.black),
            ('BACKGROUND',(0,0),(0,0),colors.black),
            ('BACKGROUND',(0,2),(0,2),c20_bg),
#            ('TEXTCOLOR',(0,0),(0,0),colors.red),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
            ('TOPPADDING',(0,0),(-1,-1),ipad),
            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ])

        cardcells.append(cc)

    line=[]
    data=[]
    for t in cardcells:
        line.append(t) 
        if len(line)==2:
            data.append(line)
            line=[]

    if len(line)>0:
        line.extend((2-len(line))*" ")
        data.append(line)
   
    rows = len(data) 

    if rows==0:
        elements = []
        elements.append(Paragraph(u"žádné karty",styleN))
        doc.build(elements)
        return



    bigtable = Table(data,colWidths=[8.5*cm,8.5*cm], rowHeights= rows*[5.43*cm], style=[
        ('GRID',(0,0),(-1,-1),0.5,colors.gray),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),pad),
        ('RIGHTPADDING',(0,0),(-1,-1),pad),
        ('TOPPADDING',(0,0),(-1,-1),pad),
        ('BOTTOMPADDING',(0,0),(-1,-1),pad),
    ]) 
    elements.append(bigtable)
   

    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
    doc.build(elements)

def students_invitation(output,invitations,mode='A'):


    
    if mode == 'A' or mode is None:
        dims = {'topMargin':1*cm, 'bottomMargin':1.2*cm, 'rowHeight':3*cm, 'colWidth':7*cm} 
    elif mode == 'B':
        dims = {'topMargin':0.4*cm, 'bottomMargin':0*cm, 'rowHeight':3.2*cm, 'colWidth':7*cm} 
    else:
        return
    

    width = 150
    height = 12
    ipad = 1
    pad = 5

    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=0, rightMargin=0, topMargin=dims['topMargin'], bottomMargin=dims['bottomMargin'], showBoundary=0)
    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']
    styleP = styles['Post']




    elements = []

    invs = []
    for i in invitations:
        p_lines = i.get_print_lines()         
        pl_0 = Paragraph(escape(p_lines[0]),styleP)
        pl_1 = Paragraph(escape(p_lines[1]),styleP)
        pl_2 = Paragraph(escape(p_lines[2]),styleP)
        pl_3 = Paragraph(escape(p_lines[3]),styleP)
        invtable = Table([ [pl_0],[pl_1],[pl_2],[pl_3] ], colWidths=[width],rowHeights=4*[height], style=[
        #    ('GRID',(0,0),(-1,-1),0.5, colors.gray),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
            ('TOPPADDING',(0,0),(-1,-1),ipad),
            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),

            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ])

        invs.append(invtable)
       
    line=[]
    data=[]
    for t in invs:
        line.append(t) 
        if len(line)==3:
            data.append(line)
            line=[]

    if len(line)>0:
        line.extend((3-len(line))*" ")
        data.append(line)
   
    rows = len(data) 

    if rows==0:
        elements = []
        elements.append(Paragraph(u"žádná adresy",styleH))
        doc.build(elements)
        return


    bigtable = Table(data,colWidths=3*[dims['colWidth']],rowHeights= rows*[dims['rowHeight']], style=[
#        ('GRID',(0,0),(-1,-1),0.5,colors.gray),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),pad),
        ('RIGHTPADDING',(0,0),(-1,-1),pad),
        ('TOPPADDING',(0,0),(-1,-1),pad),
        ('BOTTOMPADDING',(0,0),(-1,-1),pad),
    ]) 
    elements.append(bigtable)
   

    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
     
 
    doc.build(elements)




def pdftest(output):
    logging.info('pdftest')

    c = canvas.Canvas(output)    
    c.setFont('DejaVuSansBold', 16)
    c.drawString(100,100,TEST_TEXT)

    c.showPage()
    c.save()
    logging.info('ok')    


    
