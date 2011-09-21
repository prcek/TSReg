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
    finish_error = db.BooleanProperty(default=False)
    name = db.StringProperty(default='')
    owner = db.StringProperty(default='')

    @staticmethod
    def list():
        return Job.all().order('create_datetime')
    
    @staticmethod
    def list_active():
        return Job.all().filter('active',True).order('create_datetime')
 
    @staticmethod
    def list_error():
        return Job.all().filter('finish_error',True).order('create_datetime')
 
    def init(self,name,target=None, owner=None):
        self.name = name
        self.onwer = owner
        self.active = True
        self.finish_target = target
        self.create_datetime =  datetime.datetime.utcnow()

    def start(self):
        self.start_datetime = datetime.datetime.utcnow()

    def finish(self, error=False):
        self.active = False
        self.finish_datetime = datetime.datetime.utcnow()
        self.finish_error = error

    
       

class Card(BaseModel):
    create_datetime = db.DateTimeProperty()
    owner = db.StringProperty(default='')
    name = db.StringProperty(default='')
    surname = db.StringProperty(default='')
    season_name = db.StringProperty(default='')
    course_code = db.StringProperty(default='')
    info_line_1 = db.StringProperty(default='')
    info_line_2 = db.StringProperty(default='')


    @staticmethod
    def list_all():
        return Card.all().order('create_datetime')
    
    @staticmethod
    def list_my(owner):
        return Card.all().filter('owner',owner).order('create_datetime')
 
    def init(self, owner=None, name=None, surname=None, season_name=None, course_code=None, info_line_1=None, info_line_2=None):
        self.create_datetime = datetime.datetime.utcnow()
        self.owner = owner
        self.name = name
        self.surname = surname
        self.season_name = season_name
        self.course_code = course_code
        self.info_line_1 = info_line_1
        self.info_line_2 = info_line_2
        

 

