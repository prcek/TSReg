# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Student,Course
from admin.models import Job,Card,Invitation
import utils.config as cfg
import utils.mail as mail
from google.appengine.api import mail as gmail
from google.appengine.api import taskqueue
import admin.inflector as inflector



import logging


def send_student_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    if student is None:
        logging.info('student is None')
        raise Http404
#    logging.info('student=%s'%(student))

    course = student.get_course()

 #   logging.info('course=%s'%(course))

    template_key = request.POST['template_key']
    if template_key is None:
        logging.info('template_key is None')
        raise Http404 

  #  logging.info('template_key=%s'%(template_key))

    if not template_key in mail.MAIL_TEMPLATES:
        logging.info('template_key is not valid')
        raise Http404

    sender = cfg.getConfigString('ENROLL_EMAIL',None)

    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')

    recipient = student.email.__str__()
 
    (subject,body) = mail.prepare_email_text(template_key, student,course)

    gmail.send_mail(sender, recipient, subject,body) 
    
    logging.info('send ok')

    return HttpResponse('ok')


def _obs_send_check_email(request):
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

def _obs_send_confirm_email(request):
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

def _obs_send_enroll_yes_email(request):

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

def _obs_send_enroll_no_email(request):

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


def recount_course_capacity(course):
   
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
        m = False
        f = False
        if s.addressing == 'p':
            m=True
        elif s.addressing == 's' or s.addressing == 'd':
            f=True


        if s.status == 's':
            pending+=1
            if m:
                pending_m+=1
            if f:
                pending_f+=1
            if s.paid_ok:
                pending_p+=1
                
        elif s.status == 'e':
            enrolled+=1
            if m:
                enrolled_m+=1
            if f:
                enrolled_f+=1
 
            if not s.paid_ok:
                pending_payment+=1
            else:
                enrolled_p+=1


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



    pend_open = True
    if (course.pending_limit!=-1):
        if (course.pending>=course.pending_limit):
            pend_open = False


    cap_open = True
    if (course.capacity!=-1):
        if (course.usage>=course.capacity):
            cap_open = False


    course.suspend = not (cap_open or pend_open)


def recount_capacity(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    
    if course is None:
        raise Http404
    
    recount_course_capacity(course)
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

def transfer_student(student_id, course):
    logging.info('transfer student %d'%student_id)
    student = Student.get_by_id(student_id)
    if student is None:
        return

    student.set_course_key(str(course.key()))
    student.save()
    

def transfer_students(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()



    student_ids = request.POST.getlist('student_ids')
    target_course_id = request.POST['target_course_id']
    source_course_id = request.POST['source_course_id']



    target_course = Course.get_by_id(int(target_course_id))
    if target_course is None:
        logging.info('missing target course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')

    source_course = Course.get_by_id(int(source_course_id))
    if source_course is None:
        logging.info('missing source course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')



    logging.info('student list %s'%student_ids) 
    for student_id in student_ids:
        transfer_student(int(student_id), target_course) 
    
    recount_course_capacity(source_course)
    source_course.save()
    logging.info(source_course)
 

    taskqueue.add(url='/task/recount_capacity/', params={'course_id':target_course.key().id()})


    job.finish()
    job.save()

    return HttpResponse('ok')


def prepare_card(owner, student_id, season_name, course_code, info_line_1, info_line_2):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return
  
 
    card = Card() 
    card.init(owner=owner,name=student.name, surname=student.surname, season_name=season_name,  course_code=course_code, info_line_1=info_line_1, info_line_2=info_line_2)
    card.save()
    logging.info('card=%s'%card)

def prepare_cards(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']
    season_name = request.POST['season_name']
    course_code = request.POST['course_code']
    info_line_1 = request.POST['info_line_1']
    info_line_2 = request.POST['info_line_2']


    logging.info('student list %s'%student_ids) 
    for student_id in student_ids:
        prepare_card(owner, student_id, season_name, course_code, info_line_1, info_line_2)        
    


    job.finish()
    job.save()

    return HttpResponse('ok')

def prepare_invitation(owner, student_id, mode, addressing_parents, addressing_p, addressing_s, addressing_d):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return
  

    logging.info('student: %s'%student)

    addressing=''
    iname = None
    isurname = None
    if mode=='parents':
        addressing=addressing_parents
        sex=student.get_sex()
        if not student.name is None:
            iname = inflector.do_inflect('name',sex,student.name)
        
        if not student.surname is None:
            isurname = inflector.do_inflect('surname',sex,student.surname)

    elif mode=='direct':
        if student.addressing =='p':
            addressing=addressing_p
        elif student.addressing =='s':
            addressing=addressing_s
        elif student.addressing =='d':
            addressing=addressing_d
       
    logging.info('addressing:%s'%addressing) 
 
    invitation = Invitation() 
    
    invitation.init(owner=owner,mode=mode, addressing=addressing, name=student.name, surname=student.surname, sex=student.get_sex(), street=student.street,
        street_no=student.street_no, city=student.city, post_code=student.post_code
                )

    if not iname is None:
        invitation.name_inflected = iname
    if not isurname is None:
        invitation.surname_inflected = isurname


    logging.info('pre save invitation=%s'%invitation)

    invitation.save()
    logging.info('invitation=%s'%invitation)


def prepare_invitations(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']
    mode = request.POST['mode']
    addressing_parents = request.POST['addressing_parents']
    addressing_p = request.POST['addressing_p']
    addressing_s = request.POST['addressing_s']
    addressing_d = request.POST['addressing_d']


    inflector.init_dicts()
    

    logging.info('student list %s'%student_ids) 
    for student_id in student_ids:
        prepare_invitation(owner, student_id, mode,addressing_parents, addressing_p, addressing_s, addressing_d)        


    job.finish()
    job.save()

    return HttpResponse('ok')

