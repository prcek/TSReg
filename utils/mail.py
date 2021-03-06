# -*- coding: utf-8 -*-

#from google.appengine.api import mail
from utils import config
from django.template.loader import get_template
from django.template import Context

#from string import Template
import logging
import re

email_re1 = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain


def valid_email(e):
    if e is None:
        return False

    if email_re1.match(e):
        return True
    else:
        return False 

   # return re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e)

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

def prepare_email_text(mail_key, student,course,partner=None):
    subject_n = "email/%s_subject.txt"%mail_key
    body_n= "email/%s_body.txt"%mail_key
    
    subject_t = get_template(subject_n)
    body_t = get_template(body_n)
    
    c = Context({"course": course, "student": student, "partner": partner})

    subject = subject_t.render(c)    #jen prvni radek!
    body = body_t.render(c)    
    
#    from django.utils.safestring import mark_safe, SafeUnicode
#    logging.info(type(subject))
#    logging.info(type(unicode(subject)))

#    x = u'%s'%(unicode(subject))
#    x = u'xxš'.encode('utf8')

 #   logging.info(type(x))
#    logging.info(u'šěčxxx')


#    subject = mark_safe(subject)
#    subject = unicode(subject)
#    logging.info(unicode(SafeUnicode(subject).decode('utf8')))
    
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
    'ENROLL_OK_PAY_REQUEST',
    'ENROLL_OK_SPARE',
    'ENROLL_TRANSFER',
    'ENROLL_KICK',
    'ENROLL_KICK_TO_SPARE',
    'ENROLL_FORM_REPORT',
    'ENROLL_PAY_INFO',
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
    

        



