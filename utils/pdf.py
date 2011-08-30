# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs/reportlab.zip')
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'

pdfmetrics.registerFont(TTFont('DejaVuSansMono', os.path.join(folderFonts,'DejaVuSansMono.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(folderFonts,'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', os.path.join(folderFonts,'DejaVuSansBold.ttf')))


TEST_TEXT = "Příliš žluťoučký kůň úpěl ďábelské ódy"

import logging
import StringIO

def pdftest(output):
    logging.info('pdftest')

    c = canvas.Canvas(output)    
    c.setFont('DejaVuSansBold', 16)
    c.drawString(100,100,TEST_TEXT)

    c.showPage()
    c.save()
    logging.info('ok')    

    
