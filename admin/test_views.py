# -*- coding: utf-8 -*-


from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

from google.appengine.ext import db
from google.appengine.api import taskqueue

import logging
import datetime
from django.utils import simplejson as json

#import base64
from utils.locale import local_timezone

#from google.appengine.api.urlfetch import Fetch,PUT
#from enroll.models import Course,Folder,Season,FolderStats
import utils.pdf
import utils.cdbsync as cdbsync
import utils.qrg as qrg
from enroll.models import Season,Student,StudentInvCard,Course,Folder

import utils.gid_pool as gid_pool


def plan_update_all_students(request):
    taskqueue.add(url='/task/update_all_students/')
    return HttpResponse('ok')

def plan_update_all_folders(request):
    logging.info("update_all_folders")
    folders = Folder.list()
    for f in folders:
        logging.info("folder %s"%f.key())
        cdbsync.plan_cdb_put(f)
    return HttpResponse('ok')

def plan_update_all_seasons(request):
    logging.info("update_all_seasons")
    seasons = Season.list()
    for s in seasons:
        logging.info("season %s"%s.key())
        cdbsync.plan_cdb_put(s)
    return HttpResponse('ok')

def plan_update_all_courses(request):
    logging.info("update_all_courses")
    courses = Course.list()
    for c in courses:
        logging.info("course %s"%c.key())
        cdbsync.plan_cdb_put(c)
    return HttpResponse('ok')


def qrtest(request):
    utils.pdf.qrtest()
    return HttpResponse('ok')

def test_txn(request):
    gid_pool.txn_test()
    return HttpResponse('ok')

def kill_one(student_key):

    xg_on = db.create_transaction_options(xg=True)

    def txn():
        student = Student.get(student_key)
        inv = StudentInvCard()
        inv.init(student,"sys",u"špatně vygenerovaná karta (duplicitní)")
        inv.ref_gid_in_pool = True
        inv.save()

        student.ref_gid = gid_pool.ret_and_create_new_git_item("students",student.ref_gid,str(student.key()))

        #gid_pool.ret_existing_gid_item("students",student.ref_gid,str(student.key()))
        #tudent.ref_gid=gid_pool.create_new_gid_item("students",str(student.key()))

        student.save()
        return (inv,student)


    (inv,student) = db.run_in_transaction_options(xg_on, txn)

    cdbsync.plan_cdb_put(inv)
    cdbsync.plan_cdb_put(student)


def kill_one_dupl(request):

    res = ""

    ref_gid = gid_pool.get_first_dupl("students")
    res += " val %d" % ref_gid
    if (ref_gid == -1):
        return HttpResponse(res)


    q = Student.all()
    q.filter('ref_gid =',ref_gid)
    for s in q:
        sn=s.course_season()
        res += " student %s %s %s" %(s.name,s.surname,sn) 
        kill_one(s.key())




    return HttpResponse(res)

def get_dupl_stat(request):
    res=gid_pool.get_stat("students")
    return HttpResponse(res)

def kill_multi_dupl(request):
    for i in range(100):
        taskqueue.add(queue_name='showsync', url='/admin/sys/test/kill_one_dupl/')
    return HttpResponse('ok')


def index(request):

    tz = local_timezone #pytz.timezone('Europe/Prague') 
   
    now = datetime.datetime.utcnow() 

    logging.info(now)
    logging.info(tz)
    localized_now = tz.localize(now)
    local_now = tz.fromutc(now)
    logging.info(local_now)
    local_s = local_now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(local_s)

    lines = []
    for i in range(10):
        lines.append({'key':i,'value':'v_%d'%i})


    target_response = ''
    target_group = ''
    target_value = ''

    qrg_res = "off"
    if qrg.qrg_cfg_get_on():
      qrg_res = qrg.qrg_get_info()



    if request.method == 'POST':
        logging.info(request.POST)
        target_group = request.POST['target_group']
        target_value = int(request.POST['target_value'])
        if (target_value>0):
          usage = gid_pool.put_existing_gid_item(target_group,target_value)
          target_response = "put ok (%d)" % (usage)
        elif (target_value<0):
          usage = gid_pool.ret_existing_gid_item(target_group,-target_value)
          target_response = "ret ok (%d)" % (usage)
        else:
          val = gid_pool.create_new_gid_item(target_group)
          target_response = "new ok (%d)" % (val)

  
    return render_to_response('admin/test.html', RequestContext(request, { 'qrg_res':qrg_res, 'now': now, 'localized_now': localized_now, 'local_now': local_now, 'target_group':target_group, 'target_value': target_value, 'target_response': target_response}))

