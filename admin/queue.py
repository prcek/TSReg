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

    if student.no_email_info:
        logging.info('info emails disabled for this student, ignore request') 
        return

    if not template_key in mail.MAIL_TEMPLATES:
        logging.info('plan_send_student_email - invalid template - "%s"'%template_key)
        raise Http404

    if student is None:
        logging.info('plan_send_student_email - student is None!')
        raise Http404

    taskqueue.add(url='/task/send_student_email/', params={'template_key':template_key,'student_id':student.key().id()})


def plan_update_course(course):
    if not course is None:
        if isinstance(course,Course): 
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})
        elif isinstance(course,(int,basestring)):
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course})
        else:            
            logging.info('plan_recount_course - course is wrong')
            raise Http404
    else:
        logging.info('plan_recount_course - course is None, skip')


def plan_job_transfer_students(student_ids,source_course, target_course):
    logging.info('transfer %s from course %d to course %d'%(student_ids,source_course.key().id(), target_course.key().id()))    

    job = Job()
    job.init("transfer_students",target='../../')
    job.save()
 
    taskqueue.add(url='/task/transfer_students/', params={'job_id':job.key().id(), 'student_ids':student_ids, 'course':target_course})

    logging.info('job_id %d'%(job.key().id())) 

    return job.key().id()


