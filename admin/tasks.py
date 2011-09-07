# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Student,Course
import utils.config as cfg
import utils.mail as mail
from google.appengine.api import mail as gmail


import logging

def send_check_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    
    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_check_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)

    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')

    recipient = student.email.__str__()
    
    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))
   
    gmail.send_mail(sender, recipient, subject,body) 
    
    logging.info('send ok')

    return HttpResponse('ok')

def send_confirm_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    
    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_confirm_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()
    
    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))
   
    gmail.send_mail(sender, recipient, subject,body) 
    
    logging.info('send ok')

    return HttpResponse('ok')

def send_enroll_yes_email(request):

    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    
    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_enroll_yes_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()
    
    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))
   
    gmail.send_mail(sender, recipient, subject,body) 
    
    logging.info('send ok')

    return HttpResponse('ok')

def send_enroll_no_email(request):

    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    
    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_enroll_no_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()
    
    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))
   
    gmail.send_mail(sender, recipient, subject,body) 
    
    logging.info('send ok')

    return HttpResponse('ok')


def recount_capacity(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    
    if course is None:
        raise Http404
    pending = 0
    pending_m = 0
    pending_f = 0
    pending_p = 0
    enrolled = 0
    enrolled_m = 0
    enrolled_f = 0
    enrolled_p = 0
    pending_payment = 0
    list = Student.list_for_course(course.key())
    for s in list:
#        logging.info(s)
        m = False
        f = False
        if s.addressing == 'p':
            m=True
#            logging.info('male')
        elif s.addressing == 's' or s.addressing == 'd':
            f=True
#            logging.info('female')


        if s.status == 'nc':
            pending+=1
#            logging.info('spare')
            if m:
                pending_m+=1
            if f:
                pending_f+=1
            if s.paid_ok:
#                logging.info('paid')
                pending_p+=1
                
        elif s.status == 'e':
#            logging.info('enrolled')
            enrolled+=1
            if m:
                enrolled_m+=1
            if f:
                enrolled_f+=1
 
            if not s.paid_ok:
                pending_payment+=1
            else:
 #               logging.info('paid')
                enrolled_p+=1

  #      logging.info('iiii - capacity stats: %d/%d, %d/%d, %d/%d'%( enrolled_m, pending_m, enrolled_f, pending_f, enrolled_p, pending_p))

    course.pending=pending
    course.pending_payment=pending_payment
    course.usage=enrolled

    course.stat_e_m = enrolled_m
    course.stat_s_m = pending_m
    course.stat_e_f = enrolled_f
    course.stat_s_f = pending_f
    course.stat_e_p = enrolled_p
    course.stat_s_p = pending_p

    logging.info('capacity stats: %d/%d, %d/%d, %d/%d'%( enrolled_m, pending_m, enrolled_f, pending_f, enrolled_p, pending_p))



    if (course.pending_limit!=-1):
        if (course.pending>=course.pending_limit):
            course.suspend = True
        else:
            course.suspend = False

#    if (course.capacity!=0):
#        if (course.usage>=course.capacity):
#            course.suspend = True
#        else:
#            course.suspend = False


    course.save()
    logging.info(course)
 
    return HttpResponse('ok')


def hide_course_students(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    
    if course is None:
        raise Http404
 
    list = Student.list_for_course(course.key())
    for s in list:
        s.hidden = True
        s.save()
 
    return HttpResponse('ok')
