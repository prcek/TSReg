#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


import os,sys
os.chdir('../')
sys.path.insert(0,'.')

import utils.pdf
import datetime

os.chdir('tests/')




def hello_pdf():
    utils.pdf.pdftest('hello.pdf')


class FakeInvitation():
    def get_print_lines(self):
        return ['Vážení rodiče','Karla Vomáčky','Luční 789','60178 Baculov']

def test_inivitations():
    i = FakeInvitation()
    utils.pdf.students_invitation('invitations_a.pdf',27*[i],mode='A')
    utils.pdf.students_invitation('invitations_b.pdf',27*[i],mode='B')

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
    x_pair_no = 1
    reg_datetime = datetime.datetime.utcnow()
    ref_key='B4U7F2K9L2'
    surname=u'Vomáčka'
    name=u'Jaroslav'
    email = 'jarda@vomackovi.cz'
    phone = '794145457'
    course_cost = '1199'
    paid = '1199'
    pay_info ="XX/1234"
    discount = 'dův'
    school = u'Střední škola VOM'
    school_class = '4.C'
    city='Brblov'
    post_code = '45687'
    street = 'Mastná'
    street_no = '37a'
    comment = u'já se moc těším'
    student = False
    student_check = False
    partner_ref_code = 'Partner XYZ'
    def course_season(self):
        return "season"
    def course_code(self):
        return "S51"
    def course_name(self):
        return u"Základní"


    def addressing_loc(self):
        return "osl."

    def balance_due(self):
        return 123
    def is_fp(self):
        return True
    

def test_students_table():
    course = FakeCourse()
    student = FakeStudent()
    student_2 = FakeStudent()
    student_3 = FakeStudent()
    student_2.student = True
    student_2.student_check = True
    course.group_mode = 'School'
    utils.pdf.students_table('students_table_1.pdf',course,20*[student])
    course.group_mode = 'Single'
    utils.pdf.students_table('students_table_2.pdf',course,20*[student,student_2])
    course.group_mode = 'Pair'
    utils.pdf.students_table('students_table_3.pdf',course,20*[student,student_2,student_3])


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
    student2 = FakeStudent()
    student2.reg_datetime = datetime.datetime.utcnow()

    student2.comment = "0123456778890123 sadjklfh kjashkashdjkfh kasdhfawehlkrh we  we iwheih ask jk a klskdj kwkjakejrfh wka ek akjh "
    utils.pdf.students_enroll_multi('students_enroll.pdf',8*[student,student2])
    

if __name__ == "__main__":
    hello_pdf()
    test_inivitations()
    test_students_table()
    test_students_card()
    test_students_enroll()

