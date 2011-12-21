# -*- coding: utf-8 -*-

from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api.app_identity import get_application_id
import datetime
import logging
import random

from utils import cache
from utils import crypt

from string import maketrans


def nonone(s):
    if s is None:
        return ""
    return s


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
    def keys_all():
        return Card.all(keys_only=True)
    
    @staticmethod
    def list_my(owner):
        return Card.all().filter('owner',owner).order('create_datetime')
 
    @staticmethod
    def keys_my(owner):
        return Card.all(keys_only=True).filter('owner',owner)
 
    def init(self, owner=None, name=None, surname=None, season_name=None, course_code=None, info_line_1=None, info_line_2=None):
        self.create_datetime = datetime.datetime.utcnow()
        self.owner = owner
        self.name = name
        self.surname = surname
        self.season_name = season_name
        self.course_code = course_code
        self.info_line_1 = info_line_1
        self.info_line_2 = info_line_2
        

class Invitation(BaseModel):
    create_datetime = db.DateTimeProperty()
    owner = db.StringProperty(default='')
    mode =  db.StringProperty(choices=['direct','parents'], default='direct')

    sex = db.StringProperty(choices=['-','m','f'], default='-')
    name = db.StringProperty(default='')
    surname = db.StringProperty(default='')
 
    street = db.StringProperty(default='')
    street_no = db.StringProperty(default='')
    city = db.StringProperty(default='')
    post_code = db.StringProperty(default='')
 
    addressing = db.StringProperty(default='')
    name_inflected = db.StringProperty(default='')
    surname_inflected = db.StringProperty(default='')

    @staticmethod
    def list_all():
        return Invitation.all().order('create_datetime')


    @staticmethod
    def keys_all():
        return Invitation.all(keys_only=True)
    
    @staticmethod
    def list_my(owner):
        return Invitation.all().filter('owner',owner).order('create_datetime')
 
    @staticmethod
    def keys_my(owner):
        return Invitation.all(keys_only=True).filter('owner',owner)


    def get_sex_loc(self):
        if self.sex == 'm':
            return 'muž'
        elif self.sex == 'f':
            return 'žena'
        else:
            return '?'

    def get_mode_loc(self):
        if self.mode == 'direct':
            return 'přímá'
        elif self.mode == 'parents':
            return 'rodičům'
        else:
            return '?'
 

    def get_print_lines(self):
        line_0 = self.addressing
        if line_0 is None:
            line_0 = ""
        if self.mode == 'parents':
            line_1 = "%s %s"%(nonone(self.name_inflected), nonone(self.surname_inflected))
        else:
            line_1 = "%s %s"%(nonone(self.name),nonone(self.surname))

        if self.street is None or (self.street.strip() == ""):
            line_2 = "%s %s"%(nonone(self.city), nonone(self.street_no))
            line_3 = "%s"%(nonone(self.post_code))
        else:
            line_2 = "%s %s"%(nonone(self.street), nonone(self.street_no))
            line_3 = "%s %s"%(nonone(self.post_code), nonone(self.city))
 
         
        return [line_0,line_1,line_2,line_3]

    def init(self, owner=None, mode=None, sex=None, name=None, surname=None, street=None, street_no=None, city=None, post_code=None, addressing=None):
        self.create_datetime = datetime.datetime.utcnow()
        self.owner = owner
        self.mode = mode 
        self.sex= sex
        self.name=name
        self.surname=surname
        self.street=street
        self.street_no = street_no
        self.city=city
        self.post_code = post_code
        self.addressing = addressing
 
class Inflect(BaseModel):
    create_datetime = db.DateTimeProperty()
    owner = db.StringProperty(default='')
    gender = db.StringProperty(choices=['-','m','f'], default='-')
    part = db.StringProperty(choices=['-','name','surname'], default='-') 
    pattern = db.StringProperty(default='') 
    proposal = db.StringProperty(default='')

    @staticmethod
    def list():
        return Inflect.all().order('create_datetime')

    @staticmethod
    def keys_all():
        return Inflect.all(keys_only=True)
 

    def init(self, owner=None, gender=None, part=None, pattern=None, proposal=None):
        self.create_datetime = datetime.datetime.utcnow()
        self.owner = owner
        self.gender=gender
        self.part=part
        self.pattern=pattern
        self.proposal=proposal

class FileBlob(BaseModel):
    create_datetime = db.DateTimeProperty()
    tmp = db.BooleanProperty(default=False)
    owner = db.StringProperty(default='')
    name = db.StringProperty(default='')
    data = db.BlobProperty()
    def init(self, data, owner=None, tmp=False, name=None):
        self.create_datetime = datetime.datetime.utcnow()
        self.owner = owner
        self.name = name
        self.tmp = tmp
        self.data = data
      
class CourseBackup(BaseModel):
    create_datetime = db.DateTimeProperty()
    data = db.BlobProperty()
    course_key = db.StringProperty()
    info = db.StringProperty(default='')
    filename = db.StringProperty(default='')
    def init(self, data, course):
        self.create_datetime = datetime.datetime.utcnow()
        self.course_key = str(course.key())
        self.info = "%s %s %s"%(course.code,course.folder_name(), course.season_name())
        self.filename = "kurz_%s.csv"%(course.code)
        self.data = data

    @staticmethod
    def list_for_course(course_key):
        return CourseBackup.all().filter('course_key',course_key).order('-create_datetime')
 

class AppUser(BaseModel):
    active = db.BooleanProperty()
    name = db.StringProperty()
    email = db.StringProperty()
    edit = db.BooleanProperty()
    pay = db.BooleanProperty()
    power = db.BooleanProperty()

    @staticmethod
    def list_all():
        return AppUser.all().order('email')

    @staticmethod
    def get_auth_dict():
        d = cache.get('auth_dict')
        if d is None:
            q = AppUser.all().filter('active',True)
            d = dict()       
            for u in q:
                d[u.email]=u
            cache.set('auth_dict',d)
        return d
    @staticmethod
    def flush_auth_dict():
        cache.delete('auth_dict')



class EMailList(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    emails = db.StringListProperty()


    @staticmethod
    def list_all():
        return EMailList.all().order('name')


    @staticmethod
    def get_EMAILLIST_CHOICES():
        el = EMailList.list_all()
        res = []
        for l in el:
            res.append((l.key().__str__(),l.name))
        return res


class EMailTemplate(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    valid = db.BooleanProperty(default=False)
    locked = db.BooleanProperty(default=False)
    data = db.BlobProperty()
    data_datetime = db.DateTimeProperty()
    data_size = db.IntegerProperty(default=0)

    @staticmethod
    def list_all():
        return EMailTemplate.all().order('name')

    def import_email(self):
        return "import-email-%d@%s.%s"%(self.key().id(),get_application_id(),'appspotmail.com')
 

    def setData(self,data):
        self.data_datetime = datetime.datetime.utcnow()
        self.data = data
        self.data_size = len(data)
        self.locked = True
#TODO set data and data_size

