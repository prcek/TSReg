# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Student,Course
import utils.config as cfg
from google.appengine.api import taskqueue

import datetime
import logging

def clean_expired_enrolls(request):
    now = datetime.datetime.utcnow()
    exp_min = cfg.getConfigInt('ENROLL_CHECK_TIMEOUT_MINUTES',60)
    td = datetime.timedelta(minutes=exp_min)
    lim = now-td
    list = Student.list_for_cleanup(lim).fetch(20)
    for s in list:
        rd = s.reg_datetime
        logging.info('id: %s, rd:%s, now:%s, lim:%s'%(s.key().id(),rd,now,lim))
        s.delete()
    
    return HttpResponse('ok')


def check_for_course_backup(request):
    if not cfg.getConfigBool('BACKUP_ON',False):
        logging.info('BACKUP_ON is OFF!')
        return HttpResponse('ok')
    
    now = datetime.datetime.utcnow()
    exp_min = cfg.getConfigInt('BACKUP_CHECK_MINUTES',180)
    td = datetime.timedelta(minutes=exp_min)
    lim = now-td
    course_list = Course.list_for_backup_check(lim).fetch(100)
    for c in course_list:
        logging.info('course: %s'%c)
        if c.backup_datetime is None:
            c.backup_flag = True
            c.save()
            logging.info('marked for backup') 
        elif c.backup_datetime < c.modify_datetime:
            c.backup_flag = True
            c.save()
            logging.info('marked for backup') 
 
    return HttpResponse('ok')

def plan_course_backup(request):
    if not cfg.getConfigBool('BACKUP_ON',False):
        logging.info('BACKUP_ON is OFF!')
        return HttpResponse('ok')
 
    course_list = Course.list_for_backup().fetch(100)
    for c in course_list:
        logging.info('course: %s'%c)
        taskqueue.add(url='/task/course_backup/', params={'course_id':c.key().id()})
 
    return HttpResponse('ok')
 
