#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


import os,sys
os.chdir('../')
sys.path.insert(0,'.')

import utils.pdf

os.chdir('tests/')


def hello_pdf():
    utils.pdf.pdftest('hello.pdf')

if __name__ == "__main__":
    hello_pdf()

