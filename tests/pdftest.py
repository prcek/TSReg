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
    student = False
    student_check = False

def test_students_table():
    course = FakeCourse()
    student = FakeStudent()
    student_2 = FakeStudent()
    student_2.student = True
    student_2.student_check = True
    course.group_mode = 'School'
    utils.pdf.students_table('students_table_1.pdf',course,120*[student])
    course.group_mode = 'Single'
    utils.pdf.students_table('students_table_2.pdf',course,120*[student,student_2])

if __name__ == "__main__":
    hello_pdf()
    test_inivitations()
    test_students_table()

