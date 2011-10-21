# -*- coding: utf-8 -*-

from google.appengine.api import mail
from utils import config
from string import Template
import logging
import re

def valid_email(e):
    return re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e)


def process_template(templ, student, course, signature):
    link = config.getConfigString('ENROLL_CHECK_URL_BASE','') 
    if course:
        kurz = course.code.__str__() 
    else:
        kurz = "?"

    if student:
        ref = student.ref_key.__str__()
        link+=student.confirm_key+'/' 
    else:
        ref = "?"
        link = "?"

    s = Template(templ)
    text = s.safe_substitute(link=link,ref=ref,kurz=kurz,paticka=signature)
    return text   

def prepare_email_text(mail_key, student,course):
    s = config.getConfigString('ENROLL_%s_SUBJECT'%mail_key,'')
    t = config.getConfigString('ENROLL_%s_BODY'%mail_key,'')
    sig = config.getConfigString('ENROLL_EMAIL_SIGNATURE','')
    ps = process_template(s,student,course,"")
    pt = process_template(t,student,course,sig)
    return (ps,pt)

MAIL_TEMPLATES = [
    'CHECK_EMAIL', 
    'CONFIRM_ENROLL_EMAIL', 
    'CONFIRM_ENROLL_AND_PAY_EMAIL',
    'CONFIRM_SPARE_EMAIL',
    'NOTIFY_TRANSFER_EMAIL',
    'NOTIFY_PAID_EMAIL',
    'NOTIFY_CANCEL_EMAIL',
    'NOTIFY_SPARE_EMAIL',
    'NOTIFY_KICK_EMAIL' ]
    

#def prepare_email_check(student, course):     
#    return prepare_email_text('CHECK_EMAIL',student,course)

#def prepare_email_confirm_enroll(student, course):     
#    return prepare_email_text('CONFIRM_ENROLL_EMAIL',student,course)

#def prepare_email_confirm_enroll_and_pay(student, course):     
#    return prepare_email_text('CONFIRM_ENROLL_AND_PAY_EMAIL',student,course)

#def prepare_email_confirm_spare(student, course):     
#    return prepare_email_text('CONFIRM_SPARE_EMAIL',student,course)

#def prepare_email_notify_transfer(student,course):
#    return prepare_email_text('NOTIFY_TRANSFER_EMAIL',student,course)

#def prepare_email_notify_paid(student,course):
#    return prepare_email_text('NOTIFY_PAID_EMAIL',student,course)

#def prepare_email_notify_cancel(student, course):
#    return prepare_email_text('NOTIFY_CANCEL_EMAIL',student,course)

#def prepare_email_notify_spare(student, course):
#    return prepare_email_text('NOTIFY_SPARE_EMAIL',student,course)
 
#def prepare_email_notify_kick(student, course):
#    return prepare_email_text('NOTIFY_KICK_EMAIL',student,course)
        



