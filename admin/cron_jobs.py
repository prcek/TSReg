# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Student,Course
import utils.config as cfg

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
