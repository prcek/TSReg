

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

import utils.cdbsync as cdbsync
from enroll.models import Season,Student,Course,Folder


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


    url_response = ''
    target_url = ''
    target_dskey = ''

 

    if request.method == 'POST':
        logging.info(request.POST)
        target_url = request.POST['target_url']
        target_dskey = request.POST['target_dskey']
        if target_dskey:
            key = db.Key(target_dskey)
            logging.info("target dskey %s  (kind %s id %s)" % (target_dskey,key.kind(),key.id_or_name()))
            s = db.Model.get(key)
            sd = db.to_dict(s)
            url_response = sd
            logging.info(json.dumps(sd,cls=cdbsync.DateTimeEncoder))
  #      
        else:
            url_response = cdbsync.cdb_get_db_info()
  #      utils.cdbsync.cdb_create_or_update(target_dskey)

 #       url_r = Fetch(target_url,headers={"Authorization": "Basic %s" % base64.b64encode("admin:nimda72cb")},validate_certificate=True)

  #      logging.info(url_r.status_code)
  #      logging.info(url_r.content)
  #      cdb = json.loads(url_r.content)
  #      logging.info(cdb['_id'])

  #      logging.info(cdb['seq'])
  #      cdb['seq']=cdb['seq']+1
  #      logging.info(cdb['seq'])

  #      key = db.Key(target_dskey)
  #      logging.info("target dskey %s  (kind %s id %s)" % (target_dskey,key.kind(),key.id_or_name()))
  #      s = db.Model.get(key)
  #      sd = db.to_dict(s,cdb)
  #      logging.info(json.dumps(sd))



  #      cdb_json = json.dumps(sd)
  #      logging.info(cdb_json)
  #      url_r2 = Fetch(target_url,method=PUT,payload=cdb_json,headers={"Authorization": "Basic %s" % base64.b64encode("admin:nimda72cb")} )
  #      logging.info(url_r2.status_code)
  #      logging.info(url_r2.content)


   #     url_response = '%s %d %s' % (target_url,url_r.status_code,cdb['_id'])

    return render_to_response('admin/test.html', RequestContext(request, { 'now': now, 'localized_now': localized_now, 'local_now': local_now, 'target_url':target_url, 'target_dskey': target_dskey, 'url_response': url_response}))

