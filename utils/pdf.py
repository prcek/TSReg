
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs/reportlab.zip')
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

from xml.sax.saxutils import escape

def getNow():
#    from main import getTimeZone
#    tz = getTimeZone()
#    logging.info(tz)
#    n = datetime.datetime.utcnow()
#    loc = tz.localize(n)
#    x = loc.astimezone(tz)
#    t = x.strftime("%Y-%m-%d %H:%M:%S")
#    logging.info(loc)
#    logging.info(x)
#    logging.info(t)
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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
    t=Table(data)
    t.setStyle(TableStyle([
#        ('BACKGROUND',(1,1),(-2,-2),colors.green),
#        ('TEXTCOLOR',(0,0),(1,-1),colors.red),
        ('FONT', (0,0), (-1,-1), 'DejaVuSansBold'),
        ('FONTSIZE', (0,-1), (-1,-1), 8)
    ]))
 
    elements.append(t)
    doc.build(elements)

def pdftest(output):
    logging.info('pdftest')

    c = canvas.Canvas(output)    
    c.setFont('DejaVuSansBold', 16)
    c.drawString(100,100,TEST_TEXT)

    c.showPage()
    c.save()
    logging.info('ok')    

    
