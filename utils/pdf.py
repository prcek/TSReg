
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs/reportlab.zip')
#sys.path.insert(0, 'libs')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch,mm,cm
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph

import os
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


    return stylesheet


def students_table(output,course,students):
    doc = SimpleDocTemplate(output, pagesize=A4) 
    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']


    elements = []

    elements.append(Paragraph(u"Přihlášky kurzu %s"%escape(course.code),styleH))
    elements.append(Paragraph(u"vygenerováno %s"%getNow(),styleN))


    data = [ ['č.','ref kód','přijmení','jméno'] ]
    i=1;
    for s in students:
        data.append([i,s.ref_key,s.surname,s.name])
        i+=1
   # logging.info(data) 

    #TODO: add spare students

    t=Table(data)
    t.setStyle(TableStyle([
#        ('BACKGROUND',(1,1),(-2,-2),colors.green),
#        ('TEXTCOLOR',(0,0),(1,-1),colors.red),
        ('FONT', (0,0), (-1,-1), 'DejaVuSansBold'),
        ('FONTSIZE', (0,-1), (-1,-1), 8)
    ]))
 
    elements.append(t)
    doc.build(elements)


def students_card(output,cards):
    doc = SimpleDocTemplate(output, pagesize=A4) 
    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']

    elements = []

    elements.append(Paragraph(u"legitimace....",styleH))

    doc.build(elements)

def students_invitation(output,invitations):

    width = 150
    height = 12
    ipad = 1
    pad = 5

    doc = SimpleDocTemplate(output, pagesize=A4 ,leftMargin=0, rightMargin=0, topMargin=1*cm, bottomMargin=1.2*cm, showBoundary=0)
    styles = getStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading']
    styleT = styles['Title']
    styleP = styles['Post']

    elements = []

    invs = []
    for i in invitations:
        p_lines = i.get_print_lines()         
        pl_0 = Paragraph(p_lines[0],styleP)
        pl_1 = Paragraph(p_lines[1],styleP)
        pl_2 = Paragraph(p_lines[2],styleP)
        pl_3 = Paragraph(p_lines[3],styleP)
        invtable = Table([ [pl_0],[pl_1],[pl_2],[pl_3] ], colWidths=[width],rowHeights=4*[height], style=[
            ('GRID',(0,0),(-1,-1),1, colors.red),
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
        data.append(line)
   
    rows = len(data) 
    bigtable = Table(data,rowHeights= rows*[3*cm], style=[
        ('GRID',(0,0),(-1,-1),1,colors.black),

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


    
