# -*- coding: utf-8 -*-

from google.appengine.api import taskqueue
from django.http import Http404


from enroll.models import Student,Course
from admin.models import Job
import utils.config as cfg
import utils.mail as mail
import utils.pdf as pdf
import logging
import urllib

def plan_send_student_email(template_key, student, course=None):

    if student.no_email_notification:
        logging.info('info emails disabled for this student, ignore request') 
        return

    if not mail.valid_email(student.email):
        logging.info('no valid email <%s>'%student.email)
        return

    if not template_key in mail.MAIL_TEMPLATE_KEYS:
        logging.info('plan_send_student_email - invalid template - "%s"'%template_key)
        raise Http404

    if student is None:
        logging.info('plan_send_student_email - student is None!')
        raise Http404

    taskqueue.add(url='/task/send_student_email/', params={'template_key':template_key,'student_id':student.key().id()})

def plan_send_enroll_form(student):

    if student is None:
        logging.info('plan_send_enroll_form - student is None!')
        raise Http404

    taskqueue.add(url='/task/send_enroll_form_to_admin/', params={'student_id':student.key().id()})

def plan_send_multimail(recipients,ej_id):
    logging.info('multimail job')
    taskqueue.add(queue_name='email',url='/task/plan_multimail/', params={'recipients':recipients,'ej_id':ej_id})

def plan_send_mail(recipient,ej_id):
    logging.info('single mail job %s '%(recipient))
    taskqueue.add(queue_name='email', url='/task/send_mail/', params={'recipient':recipient,'ej_id':ej_id})


def plan_update_course(course):
    if not course is None:
        if isinstance(course,Course): 
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})
        elif isinstance(course,(int,long,basestring)):
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course})
        else:            
            logging.info('plan_recount_course - course datatype is wrong - %s'%(type(course)))
            raise Http404
    else:
        logging.info('plan_recount_course - course is None, skip')


def plan_job_transfer_students(owner,student_ids,source_course, target_course):
    logging.info('transfer %s from course %d to course %d'%(student_ids,source_course.key().id(), target_course.key().id()))    

    job = Job()
    job.init("transfer_students",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/transfer_students/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids, 'source_course_id': source_course.key().id(), 'target_course_id':target_course.key().id()})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()

def plan_job_makecopy_students(owner,student_ids,source_course, target_course):
    logging.info('makecopy %s from course %d to course %d'%(student_ids,source_course.key().id(), target_course.key().id()))    

    job = Job()
    job.init("makecopy_students",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/makecopy_students/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids, 'source_course_id': source_course.key().id(), 'target_course_id':target_course.key().id()})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()


def plan_job_card_for_students(owner,student_ids,course_code, season_name, info_line_1, info_line_2):
    logging.info('prepare cards for %s, code=%s, season=%s, line1=%s, line2=%s'%(student_ids,course_code, season_name, info_line_1, info_line_2))

    job = Job()
    job.init("prepare cards",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/prepare_cards/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids, 'course_code': course_code, 'season_name':season_name, 'info_line_1':info_line_1, 'info_line_2': info_line_2})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()


def plan_job_cardout_for_students(owner,student_ids):
    logging.info('prepare cardout for %s'%(student_ids))

    job = Job()
    job.init("prepare cardout",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/prepare_cardout/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()



def plan_job_invitation_for_students(owner,student_ids,mode, addressing_parents, addressing_p,addressing_s,addressing_d):
    logging.info('prepare invitations for %s, mode=%s, addressing_parents=%s'%(student_ids,mode,addressing_parents))

    job = Job()
    job.init("prepare invitations",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/prepare_invitations/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids, 'mode': mode, 'addressing_parents':addressing_parents,
    'addressing_p':addressing_p,'addressing_s':addressing_s,'addressing_d':addressing_d})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()

def plan_job_hide_students(owner,student_ids,course):
    logging.info('hide students %s'%(student_ids))

    job = Job()
    job.init("delete students",target='../../', owner=owner)
    job.save()
 
    taskqueue.add(url='/task/hide_students/', params={'job_id':job.key().id(), 'owner':owner, 'student_ids':student_ids, 'course_id': course.key().id()})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()


