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
    utils.pdf.students_invitation('invitations.pdf',29*[i])

class FakeCourse():
    code='X123'
    name='name'
    def folder_name(self):
        return 'folder'
    def season_name(self):
        return 'season'
    group_mode = 'Single'
    

class FakeStudent():
    ref_key='ref_key'
    surname='surename'
    name='name'
    to_pay = '9999'
    balance_due = '9999'
    discount = 'dův'
    school = 'skola'
    school_class = 'trida'
    comment = 'poznamka'

def test_students_table():
    course = FakeCourse()
    course.group_mode = 'School'
    student = FakeStudent()
    utils.pdf.students_table('students_table.pdf',course,120*[student])

if __name__ == "__main__":
    hello_pdf()
    test_inivitations()
    test_students_table()

