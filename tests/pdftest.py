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
        return ['Vážení rodiče','Karla Vomáčky','Luční 789','60178 Baculov']

def test_inivitations():
    i = FakeInvitation()
    utils.pdf.students_invitation('invitations_a.pdf',4*[i],mode='A')
    utils.pdf.students_invitation('invitations_b.pdf',1*[i],mode='B')

class FakeCourse():
    code='X123'
    name='name'
    def folder_name(self):
        return 'folder'
    def season_name(self):
        return 'season'
    group_mode = 'Single'
    

class FakeStudent():
    x_pair_empty_slot = False
    x_no = 1
    x_class_no = 1
    reg_datetime = None
    ref_key='ref_key'
    surname='surename'
    name='name'
    email = 'mail'
    phone = 'telf'
    to_pay = '9999'
    balance_due = '9999'
    discount = 'dův'
    school = 'skola'
    school_class = 'trida'
    city='mesto'
    post_code = 'psc'
    street = 'ulice'
    street_no = '37a'
    comment = 'poznamka'
    student = False
    student_check = False
    partner_ref_code = 'pref'
    def course_season(self):
        return "season"
    def course_code(self):
        return "code"

    def addressing_loc(self):
        return "osl."
    

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

class FakeCard():
    name = u"Jxxxxxx"
    surname = u"Pxxxxxxxxx"
    season_name = u"XXXX/XX"
    course_code = u"X88"
    info_line_1 = u"1xxxxxxxxxxxxxxxxxxx1"
    info_line_2 = u"2xxxxxxxxxxxxxxxxxxx2"


def test_students_card():
    card = FakeCard()
    card2 = FakeCard()
    card2.course_code = "KM12"
    card3 = FakeCard()
    card3.info_line_1 = u""
    card3.info_line_2 = u""
    card4 = FakeCard()
    card4.info_line_1 = u"xxxx"
    card4.info_line_2 = u""
 
   # utils.pdf.students_card('students_card.pdf',[card,card2])
    utils.pdf.students_card('students_card.pdf',2*[card,card2,card3,card4,card2])

def test_students_enroll():
    student = FakeStudent()
    utils.pdf.students_enroll('students_enroll.pdf',3*[student])
    

if __name__ == "__main__":
    hello_pdf()
    test_inivitations()
    test_students_table()
    test_students_card()
    test_students_enroll()

