from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache

from admin.models import AppUser

from datetime import datetime, timedelta
import json
import random
import logging
import os




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


mcache = memcache.Client()

SYMBOLS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()'
def generate_sessid():
    return ''.join([SYMBOLS[random.randrange(0, len(SYMBOLS))] for i in range(64)])

class SessionDb(db.Model):
    stored_kv = db.TextProperty()
    modification_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def load_session(sessid):
        parent_key = db.Key.from_path('SESSION_ID', sessid)

        q = SessionDb.all()
        q.ancestor(parent_key)
        sessdb = q.get()

        return sessdb

    @staticmethod
    def create_session(sessid):
        parent_key = db.Key.from_path('SESSION_ID', sessid)
        sessdb = SessionDb.load_session(sessid)

        if sessdb == None:
            sessdb = SessionDb(parent=parent_key)
            sessdb.set_kv({})
            sessdb.put()

        return sessdb

    def set_kv(self, kv):
        self.stored_kv = json.dumps(kv)

    def get_kv(self):
        return json.loads(self.stored_kv)

class Session:
    def __init__(self, request):        
        self.request = request
        try:
            self.sessid = self.request.COOKIES['SESSION_ID']
        except KeyError:
            self.sessid = generate_sessid()

        self.cookie_cleared = False

        if self.get_all() == None:
            self.cookie_cleared = True
            return

        tmp_access = self.get('tmp_access')
        if tmp_access == None:
            tmp_access = str(datetime.now()).split('.')[0]
            self.set('tmp_access', tmp_access)
        elif (datetime.strptime(tmp_access, '%Y-%m-%d %H:%M:%S') <= datetime.now() - timedelta(days=1)):
            tmp_access = str(datetime.now()).split('.')[0]
            self.set('tmp_access', tmp_access)

    def __setitem__(self, key, value):
        self.set(key,value)

    def __getitem__(self, key):
        return self.get(key)


    def set(self, key, val):
        sessdb = SessionDb.load_session(self.sessid) or \
            SessionDb.create_session(self.sessid)

        stored_kv = sessdb.get_kv()
        stored_kv[key] = val

        sessdb.set_kv(stored_kv)
        sessdb.put()
        mcache.set(key=self.sessid, value=stored_kv)
        self.cookie_cleared = False

    def get(self, key):
        try:
            stored_kv = mcache.get(self.sessid)

            if stored_kv == None:
                sessdb = SessionDb.load_session(self.sessid)
                if sessdb == None:
                    return None
                else:
                    stored_kv = sessdb.get_kv()
                    mcache.set(self.sessid, stored_kv)

            value = stored_kv[key]
            return value
        except:
            return None

    def get_all(self):
        kv = mcache.get(self.sessid)
        if kv == None:
            sessdb = SessionDb.load_session(self.sessid)
            if sessdb:
                kv = sessdb.get_kv()

        return kv

    def delete(self, key):
        sessdb = SessionDb.load_session(self.sessid)
        stored_kv = sessdb.get_kv()

        if stored_kv != None:
            try:
                stored_kv.pop(key)

                sessdb.set_kv(stored_kv)
                sessdb.put()
                mcache.set(self.sessid, stored_kv)
            except:
                pass

    def clear(self):
        sessdb = SessionDb.load_session(self.sessid)
        if sessdb:
            sessdb.delete()

        mcache.delete(self.sessid)
        self.cookie_cleared = True

class SessionMiddleware:
    def process_request(self, request):
        request.session = Session(request)

    def process_response(self, request, response):
        try:
            if not request.session.cookie_cleared:
                response.set_cookie(key='SESSION_ID', value=request.session.sessid,
                                    expires=datetime.now() + timedelta(days=7))
            else:
                response.delete_cookie(key='SESSION_ID')
        except AttributeError:
            pass

        return response

