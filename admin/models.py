from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging
import random

from utils import crypt

from string import maketrans


class Job(BaseModel):
    active = db.BooleanProperty(default=False)
    create_datetime = db.DateTimeProperty()
    start_datetime = db.DateTimeProperty()
    finish_datetime = db.DateTimeProperty()
    finish_target = db.StringProperty(default='')
    name = db.StringProperty(default='')
    owner = db.StringProperty(default='')

    @staticmethod
    def list():
        return Job.all().order('create_datetime')
    
    @staticmethod
    def list_active():
        return Job.all().filter('active',True).order('create_datetime')
 
    def init(self,name,target=None):
        self.name = name
        self.active = True
        self.finish_target = target
        self.create_datetime =  datetime.datetime.utcnow()

    def start(self):
        self.start_datetime = datetime.datetime.utcnow()

    def finish(self):
        self.active = False
        self.finish_datetime = datetime.datetime.utcnow()

    
        
