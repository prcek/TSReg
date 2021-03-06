
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
#sys.path.insert(0, 'libs/reportlab.zip')
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
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing 
from reportlab.graphics import renderSVG,renderPS,renderPDF

import os
import re
import zlib
import reportlab

folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'

pdfmetrics.registerFont(TTFont('DejaVuSansMono', os.path.join(folderFonts,'DejaVuSansMono.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(folderFonts,'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', os.path.join(folderFonts,'DejaVuSansBold.ttf')))


TEST_TEXT = "Příliš žluťoučký kůň úpěl ďábelské ódy"
LONG_TEST_TEST = TEST_TEXT + " " + TEST_TEXT + " " + TEST_TEXT
EXTRA_LONG_TEST_TEST = LONG_TEST_TEST + " " + LONG_TEST_TEST + " " + LONG_TEST_TEST
import logging
import StringIO
import datetime

from utils.locale import local_timezone

#from pytz.gae import pytz

from xml.sax.saxutils import escape

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


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
                                  fontSize=10,
                                  leading=10,
                                  alignment=TA_CENTER,
                                  spaceAfter=2),
                   )

    stylesheet.add(ParagraphStyle(name='Enroll',
                                  fontName='DejaVuSansMono',
                                  fontSize=9)
                   )

    stylesheet.add(ParagraphStyle(name='EnrollHeading',
                                  parent=stylesheet['Enroll'],
                                  fontName = 'DejaVuSansBold',
                                  fontSize=18,
                                  leading=22,
                                  spaceAfter=6),
                   )

    stylesheet.add(ParagraphStyle(name='EnrollName',
                                  parent=stylesheet['Enroll'],
                                  fontName = 'DejaVuSansBold',
                                  fontSize=14,
                                  leading=18,
                                  ),
                   )

    stylesheet.add(ParagraphStyle(name='EnrollCourse',
                                  parent=stylesheet['Enroll'],
                                  fontName = 'DejaVuSansBold',
                                  fontSize=18,
                                  leading=18,
                                  ),
                   )

    stylesheet.add(ParagraphStyle(name='EnrollComment',
                                  parent=stylesheet['Enroll'],
                                  fontName = 'DejaVuSansMono',
                                  fontSize=8,
                                  ),
                   )
 



    stylesheet.add(ParagraphStyle(name='Post',
                                  fontName='DejaVuSansMono',
                                  fontSize=9)
                   )

    stylesheet.add(ParagraphStyle(name='Card',
                                  fontName='DejaVuSansBold',
                                  fontSize=9)
                   )

    stylesheet.add(ParagraphStyle(name='CardHeaderTopL', parent=stylesheet['Card'],
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
                                  )
                   )
    stylesheet.add(ParagraphStyle(name='CardHeaderTopR', parent=stylesheet['Card'],
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
                                  )
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

    stylesheet.add(ParagraphStyle(name='CardFullname', parent=stylesheet['Card'],
                                  fontSize=8,
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
                                  )
                   )
    stylesheet.add(ParagraphStyle(name='CardFullnameSmall', parent=stylesheet['Card'],
                                  fontSize=6,
                                  textColor=colors.white,
                                  alignment=TA_CENTER,
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

    stylesheet.add(ParagraphStyle(name='CardQInfoLines', parent=stylesheet['Card'],
                                  textColor=colors.black,
                                  alignment=TA_CENTER,
                                  fontSize=6
                                  )
                   )



    return stylesheet


def students_table(output,course,students):

#    if course.group_mode == 'School':
    ps = landscape(A4)
#    else:
#        ps = A4
    
    doc = SimpleDocTemplate(output, pagesize=ps, leftMargin=1*cm, rightMargin=1*cm, topMargin=3*cm, bottomMargin=1*cm) 

    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']


    elements = []

    elements.append(Paragraph(u"Kurz %s - %s - %s (%s)"%(escape(course.code),escape(course.name), escape(course.folder_name()),escape(course.season_name())),styleH))
    elements.append(Paragraph(u"lektor: %s, místo: %s, zahájení: %s, termín: %s"%(escape(course.teacher),escape(course.place), escape(course.first_period), escape(course.period)),styleN))
    elements.append(Paragraph(u"stav ke dni %s"%getNow(),styleN))
    elements.append(Paragraph(u"<br/>",styleN))


    if course.group_mode == 'School':
        widths = [ 0.8*cm, 0.8*cm, 3*cm,  4*cm,       3*cm,    1.1*cm,   1.1*cm,  2.5*cm,    2.5*cm,   5*cm,    1.2*cm, 0.5*cm,  3.0*cm ]
        data = [ ['č.',   't.č',   'kód', 'přijmení', 'jméno', 'platba', 'dopl.', 'sleva', 'pl. info', 'škola', 'třída', 'k.', 'poznámka'] ]
    elif course.group_mode == 'Pair':
        widths = [ 0.8*cm, 0.8*cm, 3*cm,  4*cm,       3*cm,    1.1*cm,   1.1*cm,  2.5*cm,   2.5*cm,    0.5*cm,  0.5*cm, 0.5*cm, 3.0*cm]
        data = [ ['č.',    'p.č',  'kód', 'přijmení', 'jméno', 'platba', 'dopl.', 'sleva', 'pl. info', 'st.',   'ov.', 'k.', 'poznámka'] ]
    else:
        widths = [ 0.8*cm, 3*cm,  4*cm,       3*cm,    1.1*cm,   1.1*cm,   2.5*cm, 2.5*cm,      0.5*cm, 0.5*cm, 0.5*cm, 3.0*cm]
        data = [ ['č.',    'kód', 'přijmení', 'jméno', 'platba', 'dopl.', 'sleva', 'pl. info', 'st.',   'ov.',  'k.', 'poznámka'] ]

    i=1
    lc = 1
    paid_mark = []
    for s in students:
        if s.x_pair_empty_slot:
            data.append([i,'---','---','','','','','',''])    
        else:
            if s.card_out:
                sco = 'V'
            else:
                sco = ''
            
            if not s.is_fp():
                paid_mark.append(lc)
            if course.group_mode == 'School':
                data.append([s.x_no,s.x_class_no,'',s.surname,s.name,s.paid,s.balance_due(),s.discount,s.pay_info,s.school,s.school_class, sco, s.comment])
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
                    data.append([s.x_no,s.x_pair_no,'',s.surname,s.name,s.paid,s.balance_due(),s.discount,s.pay_info,st,stc,sco,s.comment])
                else:
                    data.append([i,'',s.surname,s.name,s.paid,s.balance_due(),s.discount,s.pay_info,st,stc,sco,s.comment])
        i+=1
        lc+=1
   # logging.info(data) 

    if len(data)>1:
        pad = 0
        styleData = [
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
        ]
        lightred = colors.HexColor('#FFDDDD') 
        ext = [ ('BACKGROUND',(0,x),(-1,x),lightred) for x in paid_mark]

        styleData = styleData+ext 

        t=Table(data,colWidths=widths,style=styleData)
        elements.append(t)

    doc.build(elements)


def students_enroll_old(output,students,with_partner=False):
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
            rd = rd.strftime("%d.%m.%Y %H:%M")

        elements.append(Paragraph(u"Přihláška %s"%(escape(s.ref_key)),styleT))
        elements.append(Paragraph(u"čas %s, kurz %s %s %s"%(escape(rd),escape(s.course_code()),escape(s.course_name()),escape(s.course_season())),styleT))
        if s.student:
            stu = 'Ano'
        else:
            stu = 'Ne'
        data = [
            ["oslovení",s.addressing_loc()],
            ["jméno",nonone(s.name)],
            ["přijmení",nonone(s.surname)],
            ["kurzovné",nonone(s.course_cost)],
            ["student",stu],
            ["e-mail",nonone(s.email)],
            ["telefon",nonone(s.phone)],
            ["adresa","%s %s"%(nonone(s.street),nonone(s.street_no))],
            ["","%s %s"%(nonone(s.post_code),nonone(s.city))],
        ]

        if nonone(s.school) != '' or nonone(s.school_class)!= '':
            data.append(['škola',"%s, %s"%(s.school,s.school_class)])

        if (not s.partner_ref_code is None) and s.partner_ref_code != '':
            if with_partner:
                par = s.get_partner()
                if not (par is None):
                    parn = "%s %s"%(nonone(par.name),nonone(par.surname))
                else:
                    parn = " ?"          
                data.append(['partner',"%s %s"%(s.partner_ref_code, parn)])
            else:    
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


def students_enroll_old2(output,students,with_partner=False):
    doc = SimpleDocTemplate(output, pagesize=landscape(A6) ,leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=0.5*cm, showBoundary=0)
    styles = getStyleSheet()

    styleN = styles['EnrollName']
    styleH = styles['EnrollHeading']
    styleC = styles['EnrollCourse']
    styleComment = styles['EnrollComment']

    elements = []
    
    for s in students:
        rd = s.reg_datetime
        if rd is None:
            rd = '?'
        else:
            rd = rd.strftime("%d.%m.%Y %H:%M")

#        elements.append(Paragraph(u"Přihláška %s"%(escape(s.ref_key)),styleT))
#        elements.append(Paragraph(u"čas %s, kurz %s %s %s"%(escape(rd),escape(s.course_code()),escape(s.course_name()),escape(s.course_season())),styleT))

        p1 = Paragraph(u"Přihláška <font size=8>%s</font>"%(escape(s.ref_key)),styleH) 
        p2 = Paragraph(u"%s %s"%(escape(nonone(s.name)), escape(nonone(s.surname))),styleN)
        p3 = Paragraph(u"KURZ %s"%(escape(s.course_code())),styleC)
        p4 = Paragraph(u"<font size=12>%s</font>"%(escape(s.course_name())),styleC)

        if s.student:
            stu = 'Ano'
        else:
            stu = 'Ne'

        if (not s.partner_ref_code is None) and s.partner_ref_code != '':
            if with_partner:
                par = s.get_partner()
                if not (par is None):
                    parn = "%s %s"%(nonone(par.name),nonone(par.surname))
                else:
                    parn = " ?"          
                partner = u"%s (%s)"%(parn,s.partner_ref_code)
            else:    
                partner = s.partner_ref_code
        else:
            partner = ''
 
        data = [
            [p1,''],
            [p2,''],
            ["e-mail",nonone(s.email)],
            ["telefon",nonone(s.phone)],
            ["adresa","%s %s"%(nonone(s.street),nonone(s.street_no))],
            ["","%s %s"%(nonone(s.post_code),nonone(s.city))],
            ['škola',"%s, %s"%(nonone(s.school),nonone(s.school_class))],
            ["student",stu],
            ["partner",partner],
            ["kurzovné",nonone(s.course_cost)],
            ["čas",rd],
            [p3,""],
            [p4,""],
        ]


   

        ipad=0.5
        t = Table(data, colWidths=[2*cm,10*cm],
        style=[
            ('SPAN',(0,0),(1,0)),
            ('BOX',(0,0),(1,0),2,colors.black),

            ('SPAN',(0,1),(1,1)),
            ('TOPPADDING',(0,1),(1,1),10),

            ('SPAN',(0,4),(0,5)),
            ('VALIGN',(0,4),(0,5),'TOP'),

            ('SPAN',(0,11),(1,11)),
            ('SPAN',(0,12),(1,12)),

#            ('GRID',(0,0),(-1,-1),0.5, colors.gray),
            ('FONT', (1,0), (1,-1), 'DejaVuSansBold'),
            ('FONT', (0,0), (0,-1), 'DejaVuSansMono'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
            ('TOPPADDING',(0,2),(-1,-1),ipad),
            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
 
        ])
        elements.append(t)
        if (not s.comment is None) and (s.comment != ''):
            elements.append(Paragraph(u"Poznámka: %s"%(escape(nonone(s.comment))),styleComment))

        elements.append(PageBreak())
                

    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
    doc.build(elements)

def students_enroll_element(s,with_partner=False):
    styles = getStyleSheet()

    styleN = styles['EnrollName']
    styleH = styles['EnrollHeading']
    styleC = styles['EnrollCourse']
    styleComment = styles['EnrollComment']

    
    rd = s.reg_datetime
    if rd is None:
        rd = '?'
    else:
        rd = rd.strftime("%d.%m.%Y %H:%M")


    p1 = Paragraph(u"Přihláška <font size=8>%s</font>"%(escape(s.ref_key)),styleH) 
    p2 = Paragraph(u"%s %s"%(escape(nonone(s.name)), escape(nonone(s.surname))),styleN)
    p3 = Paragraph(u"KURZ %s"%(escape(s.course_code())),styleC)
    p4 = Paragraph(u"<font size=12>%s</font>"%(escape(s.course_name())),styleC)
    p5 = Paragraph(u"Poznámka: %s"%(escape(nonone(s.comment))),styleComment)

    if s.student:
        stu = 'Ano'
    else:
        stu = 'Ne'

    if (not s.partner_ref_code is None) and s.partner_ref_code != '':
        if with_partner:
            par = s.get_partner()
            if not (par is None):
                parn = "%s %s"%(nonone(par.name),nonone(par.surname))
            else:
                parn = " ?"          
            partner = u"%s (%s)"%(parn,s.partner_ref_code)
        else:    
            partner = s.partner_ref_code
    else:
        partner = ''

    data = [
            [p1,''],
            [p2,''],
            ["e-mail",nonone(s.email)],
            ["telefon",nonone(s.phone)],
            ["adresa","%s %s"%(nonone(s.street),nonone(s.street_no))],
            ["","%s %s"%(nonone(s.post_code),nonone(s.city))],
            ['škola',nonone(s.school)],
            ['třída',nonone(s.school_class)],
            ["student",stu],
            ["partner",partner],
            ["kurzovné",nonone(s.course_cost)],
            ["čas",rd],
            [p3,""],
            [p4,""],
            [p5,""],
    ]


   

    ipad=0.5
    t = Table(data, colWidths=[2*cm,10*cm],
    style=[
            ('SPAN',(0,0),(1,0)),
            ('BOX',(0,0),(1,0),2,colors.black),

            ('SPAN',(0,1),(1,1)),
            ('TOPPADDING',(0,1),(1,1),10),

            ('SPAN',(0,4),(0,5)),
            ('VALIGN',(0,4),(0,5),'TOP'),

            ('SPAN',(0,12),(1,12)),
            ('SPAN',(0,13),(1,13)),
            ('SPAN',(0,14),(1,14)),

#            ('GRID',(0,0),(-1,-1),0.5, colors.gray),
            ('FONT', (1,0), (1,-1), 'DejaVuSansBold'),
            ('FONT', (0,0), (0,-1), 'DejaVuSansMono'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
            ('TOPPADDING',(0,2),(-1,-1),ipad),
            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
 
    ])

    return t

def students_enroll(output,students,with_partner=False):
    doc = SimpleDocTemplate(output, pagesize=landscape(A6) ,leftMargin=1*cm, rightMargin=1*cm, topMargin=0.5*cm, bottomMargin=0.5*cm, showBoundary=0)
    styles = getStyleSheet()
    styleH = styles['EnrollHeading']


    elements = []
    for s in students:
        elements.append(students_enroll_element(s,with_partner))
        elements.append(PageBreak())
                

    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
    doc.build(elements)


def students_enroll_multi(output,students,with_partner=False):
    styles = getStyleSheet()

    styleH = styles['EnrollHeading']
 
    doc = SimpleDocTemplate(output, pagesize=landscape(A4) ,leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=0.5*cm, showBoundary=0)
    elist = []
    for s in students:
        elist.append(students_enroll_element(s,with_partner))


    elements = []
    if len(elist)==0:
        elements.append(Paragraph(u"žádná data",styleH))
        doc.build(elements)
        return



    line=[]
    data=[]
    for e in elist:
        line.append(e) 
        if len(line)==2:
            data.append(line)
            line=[]

    if len(line)>0:
        line.extend((2-len(line))*" ")
        data.append(line)
   
    rows = len(data) 



    cw = ((landscape(A4)[0])-2*cm)/2
    rh = ((landscape(A4)[1])-2*cm)/2
    
    t = Table(data,  colWidths=[cw,cw], rowHeights= rows*[rh],
        style=[
            ('GRID',(0,0),(-1,-1),0.5, colors.gray),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
    ])

    elements.append(t)
 
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
        
        c20 = Paragraph(nonone(info_text),styleIL)
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

def students_qcard(output,cards):
    ipad = 1
    pad = 10

    logging.info("gen qcard")
    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=1*cm, rightMargin=1*cm, topMargin=0.8*cm, bottomMargin=1*cm, showBoundary=0)
    styles = getStyleSheet()

    styleN = styles['Normal']
    styleHeaderTopL = styles['CardHeaderTopL']
    styleHeaderTopR = styles['CardHeaderTopR']
    styleHeaderLeft = styles['CardHeaderLeft']
    styleHeaderRight = styles['CardHeaderRight']
    styleIL  = styles['CardQInfoLines']
    styleSeason  = styles['CardSeason']
    styleCode = styles['CardCode']
    styleFullname = styles['CardFullname']
    styleFullnameSmall= styles['CardFullnameSmall']

    elements = []

    cardcells = []
    for c in cards:
        logging.info("gen qcard for %s" % c)
        info_empty = (c.info_line_1 is None or c.info_line_1=='') and (c.info_line_2 is None or c.info_line_2=='')
        logging.info("#0")

        unit = 29*mm
        qrw = QrCodeWidget(c.qrcode)
        logging.info("#0.1")
        logging.info("xxx")

        b = qrw.getBounds()
        logging.info( b )
        w = b[2]-b[0]
        h = b[3]-b[1]
        qrcode_image = Drawing(unit,unit,transform=[unit/w,0,0,unit/h,0,0])
        logging.info("#0.2")

        qrcode_image.add(qrw)
        logging.info("#1")
            
#        c00 = Paragraph("<font size=12>STARLET</font><br/><font size=8>TANEČNÍ ŠKOLA<br/>MANŽELŮ BURYANOVÝCH</font>",styleHeaderLeft)
#        c01 = Paragraph("ČÍSLO<br/>KURZU",styleHeaderRight)

        #c10_n = Paragraph(escape(nonone(c.name)),styleName)
        #c10_s = Paragraph(escape(nonone(c.surname)),styleSurname)


        #code = nonone(c.course_code)
        #if len(code)<=3:
        #    code_p = escape(code) 
        #else:
        #    m = re.match('([^\d]*)(.*)',code)
        #    if m:
        #        code_p = "%s<br/>%s"%(escape(m.group(1)), escape(m.group(2)))
        #    else:       
        #        code_p = escape(code)

        c01 = Paragraph(nonone(c.course_code),styleCode)
        c11 = Paragraph(nonone(c.season_name),styleSeason)
        logging.info("#2")

        #if info_empty:
        #    c20_bg = colors.white
        #else:
        #    c20_bg = colors.black

        info_text = u""
        if not (c.info_line_1 is None or c.info_line_1==''):            
            info_text = info_text+escape(c.info_line_1)

        if not (c.info_line_2 is None or c.info_line_2==''):            
            if info_text != "":
                info_text = info_text + "<br/>"
            info_text = info_text + escape(c.info_line_2)
            

        #c10 = Table([[c10_n],[c10_s]], style=[
       #     ('GRID',(0,0),(-1,-1),1, colors.black)
        #])
        
        c02 = Paragraph(nonone(info_text),styleIL)
        c03 = Paragraph(escape(nonone(c.name)+" "+nonone(c.surname)),styleFullname)
        logging.info("#3")

        #c21 = Paragraph(nonone(c.season_name),styleSeason)

#        cc = Table([ [c00,c01],[c10,qrcode_image],[c20,c21] ], colWidths=[5.9*cm,1.5*cm],rowHeights=[1.50*cm,1.95*cm,0.95*cm], style=[
#            ('GRID',(0,0),(-1,-1),1, colors.black),
#            ('BACKGROUND',(0,0),(0,0),colors.black),
#            ('BACKGROUND',(0,2),(0,2),c20_bg),
#            ('LEFTPADDING',(0,0),(-1,-1),ipad),
#            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
#            ('TOPPADDING',(0,0),(-1,-1),ipad),
#            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
#            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
#            ('ALIGN',(0,0),(-1,-1),'CENTER'),
#        ])

        c00 = Paragraph("<font size=14>STARLET</font>",styleHeaderTopL)
        c10 = Paragraph("<font size=8>TANEČNÍ ŠKOLA<br/>MANŽELŮ BURYANOVÝCH</font>",styleHeaderTopR)
       # <br/><font size=8>TANEČNÍ ŠKOLA<br/>MANŽELŮ BURYANOVÝCH</font>",styleHeaderLeft)
        logging.info("#4")


        cc = Table([ 
              [c00,c10,"#"],
              [c01,c11,qrcode_image],
              [c02,"#","#"], 
              [c03,"#","#"]],
               colWidths=[2.7*cm,2.0*cm,2.7*cm],rowHeights=[1*cm,1.7*cm,1.00*cm,0.7*cm], style=[
            #('GRID',(0,0),(-1,-1),1, colors.black),
            ('BOX',(0,0),(-1,-1),1,colors.black),
            ('SPAN',(1,0),(2,0)),  #ts line
            ('BACKGROUND',(0,0),(-1,0),colors.black),
            ('VALIGN',(0,0),(-1,0),'MIDDLE'),

            ('LINEBELOW',(0,1),(1,1),1,colors.black),
            ('LINEAFTER',(1,1),(1,2),1,colors.black),

            ('SPAN',(2,1),(2,2)),  #qr

            ('SPAN',(0,2),(1,2)),  #info line
            ('VALIGN',(0,2),(1,2),'BOTTOM'),

            ('SPAN',(0,3),(2,3)),  #name
            ('BACKGROUND',(0,3),(-1,3),colors.black),



#            ('BACKGROUND',(0,2),(0,2),c20_bg),
            ('LEFTPADDING',(0,0),(-1,-1),ipad),
            ('RIGHTPADDING',(0,0),(-1,-1),ipad),
#            ('TOPPADDING',(0,0),(-1,-1),ipad),
#            ('BOTTOMPADDING',(0,0),(-1,-1),ipad),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ])
        logging.info("#5")

        cardcells.append(cc)
        logging.info("#6")


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

    logging.info("#7")


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
   
    logging.info("#8")


    if len(elements)==0:
        elements.append(Paragraph(u"žádná data",styleH))
    doc.build(elements)


def get_qrcode_as_svg_zipstring(code_value):
  logging.info("get_qrcode_as_svg_string")

  unit = 29*mm

  qrw = QrCodeWidget(code_value)
  b = qrw.getBounds()
  logging.info( b )
  w = b[2]-b[0]
  h = b[3]-b[1]
  qrcode_image = Drawing(unit,unit,transform=[unit/w,0,0,unit/h,0,0])
  qrcode_image.add(qrw)


  rs = renderSVG.drawToString(qrcode_image)
  logging.info("raw size %d" % len(rs))
  #rsz = zlib.compress(rs)
  #logging.info("zip size %d" % len(rsz))
  return rs



def qrtest():
  logging.info("qrtest ================ START =================  qrtest")

  unit = 29*mm

  qrw = QrCodeWidget(EXTRA_LONG_TEST_TEST)


  b = qrw.getBounds()
  logging.info( b )
  w = b[2]-b[0]
  h = b[3]-b[1]
  qrcode_image = Drawing(unit,unit,transform=[unit/w,0,0,unit/h,0,0])
  qrcode_image.add(qrw)


  rs = renderSVG.drawToString(qrcode_image)
  logging.info(len(rs))
  rsz = zlib.compress(rs)
  logging.info(len(rsz))


  logging.info("qrtest ================ END =================  qrtest")


def students_invitation(output,invitations,mode='A'):


    
    if mode == 'A' or mode is None:
        dims = { 'leftMargin': 0.6*cm, 'rightMargin':0.6*cm, 'topMargin':1.5*cm, 'bottomMargin':1.2*cm, 'rowHeight':2.95*cm, 'colWidth':6.4*cm} 
    elif mode == 'B':
        dims = { 'leftMargin': 0, 'rightMargin':0, 'topMargin':0.4*cm, 'bottomMargin':0*cm, 'rowHeight':3.2*cm, 'colWidth':7*cm} 
    else:
        return
    

    width = 150
    height = 12
    ipad = 1
    pad = 5

    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=dims['leftMargin'], rightMargin=dims['rightMargin'], topMargin=dims['topMargin'], bottomMargin=dims['bottomMargin'], showBoundary=0)
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
#            ('GRID',(0,0),(-1,-1),0.5, colors.gray),
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

def empty_document(output, text):

    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=1*cm, rightMargin=1*cm, topMargin=0.8*cm, bottomMargin=1*cm, showBoundary=0)
    styles = getStyleSheet()

    styleN = styles['Normal']
    styleH = styles['Heading']
    
    elements=[]
    elements.append(Paragraph(text,styleH))
    doc.build(elements)



def pdftest(output):
    logging.info('pdftest')

    c = canvas.Canvas(output)    
    c.setFont('DejaVuSansBold', 16)
    c.drawString(100,100,TEST_TEXT)

    c.showPage()
    c.save()
    logging.info('ok')    


    
