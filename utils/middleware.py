from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

from admin.models import AppUser

from datetime import datetime, timedelta
import json
import random
import logging
import os
import uuid




class GaeInfo:
    live = False
    def __init__(self, request):
        self.live = not os.environ['SERVER_SOFTWARE'].startswith('Development') 

    

   
class AuthInfo:
    auth = False
#    wrong = False
    admin = False
    edit = False
    pay = False
    power = False
    guest = True
#    power = False
#    cron = False
#    task = False
    def __init__(self, request):
        self.gae_user = users.get_current_user()
        self.gae_admin = users.is_current_user_admin()

#        if (request.cron_request) and request.path.startswith('/cron_jobs/'):
#            logging.info('auth: cron user')
#            self.cron = True 
#            self.auth = True
            

#        if (request.task_request) and request.path.startswith('/tasks/'):
#            logging.info('auth: task request')
#            self.task = True
#            self.auth = True

#        if self.gae_user:
#            self.user = User.objects.all().filter('email =',self.gae_user.email()).get()
#        else:
#            self.user = None

        self.login_url =  users.create_login_url(request.path) 
        self.logout_url =  users.create_logout_url(request.path) 


        if self.gae_user:
            self.auth = True
            self.name = self.gae_user.nickname()
            self.email = self.gae_user.email()

            d = AppUser.get_auth_dict()
            aur = d.get(self.email)
            if aur:
                self.edit = aur.edit
                self.pay = aur.pay
                self.power = aur.power
                self.guest = False
            elif self.gae_admin:
                self.edit = True
                self.pay = True
                self.power = True
                
 

        if self.gae_admin:
            logging.info('auth: gae admin')
            self.admin = True
            
        
class Gae(object):
  def process_request(self, request):
    request.__class__.gae_info = GaeInfo(request)
    return None
    

class Auth(object):
  def process_request(self, request):
    request.__class__.auth_info = AuthInfo(request)
    if request.auth_info.auth:
        logging.info('authorised access')
#        if request.auth_info.wrong:
#            logging.info('wrong user')
#            return render_to_response('relogin.html', RequestContext(request, { }))
            
#        return HttpResponseRedirect(request.auth_info.login_url)
    return None

#class Cron(object):
#  def process_request(self, request):
#    request.__class__.cron_request = False 
#    request.__class__.task_request = False 
#    if 'HTTP_X_APPENGINE_CRON' in request.META:
#        logging.info('X-AppEngine-Cron detected. This is cron request.')
#        request.__class__.cron_request = True 
#    if 'HTTP_X_APPENGINE_QUEUENAME' in request.META:
#        logging.info('X-AppEngine-QueueName detected. This is task request.')
#        request.__class__.task_request = True 
#        
#    return None
session_ancestor_key = ndb.Key('Sessions','root')

class SessionData(ndb.Model):
    session_json = ndb.TextProperty()
    modification_time = ndb.DateTimeProperty(auto_now=True)


    def set_dict(self, kv):
        self.session_json = json.dumps(kv)

    def get_dict(self):
        return json.loads(self.session_json)




class Session:
    def __init__(self, request):        
        self.request = request
        self.session_data = None
        self.cleared = False
        self.dict = None
        self.session_id = None

        try:
            self.session_id = self.request.COOKIES['SESSION_ID']
            logging.debug('session cookie %s' % self.session_id)

        except KeyError:
            logging.debug('no session cookie')
            self.dict = dict()


    def __setitem__(self, key, value):
        self.set(key,value)

    def __getitem__(self, key):
        return self.get(key)


    def set(self, key, value):
        if self.dict is None:
            self.load_or_create()

        logging.debug('session set key %s, value %s' % (key,value))
        self.dict[key]=value


    def get(self, key, default = None):
        if self.dict is None:
            self.load_or_create()


        value = self.dict.get(key,default)
      
        logging.debug('session read key %s, value %s' % (key,value))
        return value



    def clear(self):
        self.cleared = True
        self.dict = None
        logging.debug('session cleared')

    def load_or_create(self):
        if not self.session_id:
            logging.info('session id missing, creating empty dict')
            self.dict = dict()
        else:
            try:
                logging.info('session load data for %s', self.session_id)
                self.session_data = SessionData.get_by_id(self.session_id,parent = session_ancestor_key)
                if self.session_data:
                    self.dict = self.session_data.get_dict()
                    logging.info('session data loaded')
                else:
                    logging.info('session not found')
                    self.session_id = None
                    self.dict = dict()
            except Exception as e:
                logging.error('reading session error - %s' % e)
                self.session_id = None
                self.dict = dict()





    def store(self,response):
        if self.dict:
            logging.debug('session store dict')
            if self.session_data:
                logging.debug('session data ready')
                self.session_data.set_dict(self.dict)
                self.session_data.put()
                logging.debug('session data saved')

             
            else:
                logging.debug('session data not ready')
                self.session_id = str(uuid.uuid4()) 
                self.session_data = SessionData.get_or_insert(self.session_id,parent = session_ancestor_key)
                self.session_data.set_dict(self.dict)
                key = self.session_data.put()
                logging.info('session data stored, new key is %s',key)
                
            response.set_cookie(key='SESSION_ID', value=self.session_id,        
                expires=datetime.now() + timedelta(days=7))
            logging.debug('session cookie sets %s', self.session_id)


        else:
            logging.debug('session store without dict')
            if self.cleared and self.session_id:

                response.delete_cookie(key='SESSION_ID')
               
                key = ndb.Key(SessionData,self.session_id,parent = session_ancestor_key)
                logging.info('session delete %s',key)
                key.delete()
                logging.info('session data deleted, key is %s', key)
               



        

class SessionMiddleware:
    def process_request(self, request):
        request.session = Session(request)

    def process_response(self, request, response):
        try:
            logging.debug('processing response cookies')
            request.session.store(response)
        except Exception as e:
            logging.error('session store problem - %s' % e)
            pass

        return response

