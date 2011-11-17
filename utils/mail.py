# -*- coding: utf-8 -*-

#from google.appengine.api import mail
from utils import config
from django.template.loader import get_template
from django.template import Context
#from string import Template
import logging
import re

def valid_email(e):
    if e is None:
        return False
    return re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e)

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def process_template2(template_name, student,course):
    return "XXX"        


def process_template(templ, student, course, signature):
    pass
#    link = config.getConfigString('ENROLL_CHECK_URL_BASE','') 
#    if course:
#        kurz = course.code.__str__() 
#    else:
#        kurz = "?"
#
#    if student:
#        ref = student.ref_key.__str__()
#        link+=student.confirm_key+'/' 
#    else:
#        ref = "?"
#        link = "?"
#
#    s = Template(templ)
#    text = s.safe_substitute(link=link,ref=ref,kurz=kurz,paticka=signature)
#    return text   

def prepare_email_text(mail_key, student,course):
    subject_n = "email/%s_subject.txt"%mail_key
    body_n= "email/%s_body.txt"%mail_key
    
    subject_t = get_template(subject_n)
    body_t = get_template(body_n)
    
    c = Context({"course": course, "student": student})

    subject = subject_t.render(c)    #jen prvni radek!
    body = body_t.render(c)    
    
    
    return (subject,body)
#    s = config.getConfigString('ENROLL_%s_SUBJECT'%mail_key,'')
#    t = config.getConfigString('ENROLL_%s_BODY'%mail_key,'')
#    sig = config.getConfigString('ENROLL_EMAIL_SIGNATURE','')
#    ps = process_template(s,student,course,"")
#    pt = process_template(t,student,course,sig)
#    return (ps,pt)

MAIL_TEMPLATE_KEYS = [
    'TEST', 
    'ENROLL_CHECK',
]


MAIL_TEMPLATE_KEYS_x = [
    'CHECK_EMAIL', 
    'CONFIRM_ENROLL_EMAIL', 
    'CONFIRM_ENROLL_AND_PAY_EMAIL',
    'CONFIRM_SPARE_EMAIL',
    'NOTIFY_TRANSFER_EMAIL',
    'NOTIFY_PAID_EMAIL',
    'NOTIFY_CANCEL_EMAIL',
    'NOTIFY_SPARE_EMAIL',
    'NOTIFY_KICK_EMAIL' ]
    

        



