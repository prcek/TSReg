# -*- coding: utf-8 -*-

from google.appengine.api import mail
from utils import config
from string import Template
import logging


def prepare_check_email_text(student, course):     
    link = config.getConfigString('ENROLL_CHECK_URL_BASE','')
    logging.info('link:%s'%link) 

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



    s = Template(config.getConfigString('ENROLL_CHECK_EMAIL',''))
    text = s.safe_substitute(link=link,ref=ref,kurz=kurz)
    logging.info('text=%s'%text)

    return text

def prepare_confirm_email_text(student, course):     
    if course:
        kurz = course.code.__str__() 
    else:
        kurz = "?"
    
    if student:
        ref = student.ref_key.__str__()
    else:
        ref = "?"

    s = Template(config.getConfigString('ENROLL_CONFIRM_EMAIL',''))
    text = s.safe_substitute(ref=ref,kurz=kurz)
    logging.info('text=%s'%text)

    return text

def prepare_enroll_yes_email_text(student, course):     
    if course:
        kurz = course.code.__str__() 
    else:
        kurz = "?"
    
    if student:
        ref = student.ref_key.__str__()
    else:
        ref = "?"

    s = Template(config.getConfigString('ENROLL_ENROLL_YES_EMAIL',''))
    text = s.safe_substitute(ref=ref,kurz=kurz)
    logging.info('text=%s'%text)

    return text

def prepare_enroll_no_email_text(student, course):     
    if course:
        kurz = course.code.__str__() 
    else:
        kurz = "?"
    
    if student:
        ref = student.ref_key.__str__()
    else:
        ref = "?"

    s = Template(config.getConfigString('ENROLL_ENROLL_NO_EMAIL',''))
    text = s.safe_substitute(ref=ref,kurz=kurz)
    logging.info('text=%s'%text)

    return text



