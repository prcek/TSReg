#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


import os,sys
os.chdir('../')
sys.path.insert(0,'.')

import utils.pdf

os.chdir('tests/')




def hello_pdf():
    utils.pdf.pdftest('hello.pdf')


class FakeInvitation():
    def get_print_lines(self):
        return ['Aa','Bb','Cc','Dd']

def test_inivitations():
    i = FakeInvitation()
    utils.pdf.students_invitation('out.pdf',29*[i])

if __name__ == "__main__":
    hello_pdf()
    test_inivitations()

