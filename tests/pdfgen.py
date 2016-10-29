#!/usr/bin/python2.6
 # -*- coding: utf-8 -*-

import sys
import os

pathname, scriptname = os.path.split(sys.argv[0])
sys.path.insert(0, os.path.join(pathname,'../libs/reportlab_25.zip'))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch,mm,cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'
pdfmetrics.registerFont(TTFont('DejaVuSansMono', os.path.join(folderFonts,'DejaVuSansMono.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(folderFonts,'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', os.path.join(folderFonts,'DejaVuSansBold.ttf')))


TEST_TEXT = "Příliš žluťoučký kůň úpěl ďábelské ódy"

def table_pdf():
    doc = SimpleDocTemplate("simple_table.pdf", pagesize=A4)
    elements = []
    data= [['00', '01', '02', '03', TEST_TEXT],
       ['10', '11', '12', '13', '14'],
       ['20', TEST_TEXT, '22', '23', '24'],
       ['30', '31', '32', TEST_TEXT, '34']]
    t=Table(data)
  #  t.setFont('DejaVuSansBold', 30)
    t.setStyle(TableStyle([
        ('BACKGROUND',(1,1),(-2,-2),colors.green),
        ('TEXTCOLOR',(0,0),(1,-1),colors.red),
        ('FONT', (0,0), (-1,-1), 'DejaVuSansBold'),
        ('FONTSIZE', (0,-1), (-1,-1), 8)
    ]))
    elements.append(t)
    # write the document to disk
    doc.build(elements)


def hello_pdf():
    c = canvas.Canvas(os.path.join(pathname,"hello.pdf"))
    # move the origin up and to the left
    c.translate(inch,inch)
    # define a large font
    #c.setFont("Helvetica", 80)
    c.setFont('DejaVuSansBold', 30)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
    # draw a rectangle
    c.rect(inch,inch,6*inch,9*inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.setFont('DejaVuSansBold', 20)
    c.drawString(0, -3*inch, "DejaVuSansBold %s"% TEST_TEXT)
    c.setFont('DejaVuSans', 20)
    c.drawString(0, -4*inch, "DejaVuSans %s" %TEST_TEXT)
    c.setFont('DejaVuSansMono', 20)
    c.drawString(0, -5*inch, "DejaVuSansMono %s" %TEST_TEXT)



    c.showPage()
    c.save()

if __name__ == "__main__":
    hello_pdf()
    table_pdf()
