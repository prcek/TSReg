from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from google.appengine.api import users
#from utils.models import User
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

