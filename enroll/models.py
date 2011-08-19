# -*- coding: utf-8 -*-

from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging

class Course(BaseModel):
    active = db.BooleanProperty(default=False)
    code = db.StringProperty(default='')
    name = db.StringProperty(default='')
    order_value = db.IntegerProperty(default=0)
    category = db.StringProperty(default='')
    period = db.StringProperty(default='')
    first_period = db.StringProperty(default='')
    group_mode = db.StringProperty(choices=['Single','Pair'], default='Single')
    capacity = db.IntegerProperty(default=0)
    usage = db.IntegerProperty(default=0)
    pending = db.IntegerProperty(default=0)
    pending_limit = db.IntegerProperty(default=0)
    hidden = db.BooleanProperty(default=False)
    

    @staticmethod
    def list():
        return Course.all().filter('hidden',False).order('order_value').order('code')

    @staticmethod
    def get_code_by_key(course_key):
        if course_key is None:
            return None
        c = Course.get(course_key)
        if c is None:
            return None
        return c.code

    @staticmethod
    def get_COURSE_CHOICES():
        clist = Course.list()
        res = []
        for c in clist:
            res.append((c.key(),c.code))
        return res 

    def group_mode_loc(self):
        if self.group_mode == 'Single':
            return 'jednotlivci'
        elif self.group_mode == 'Pair':
            return 'po párech'
        return '?'

class Student(BaseModel):
    hidden = db.BooleanProperty(default=False)
    course_key = db.ReferenceProperty(Course,collection_name='course_key')
    status = db.StringProperty(choices=['-','n','nc'], default='-')
    reg_datetime = db.DateTimeProperty()
    addressing = db.StringProperty(choices=['-','p','s','d'], default='-')
    name = db.StringProperty(default='')
    surname = db.StringProperty(default='')
    year = db.IntegerProperty(default=0)
    email = db.StringProperty(default='') 
    phone = db.StringProperty(default='')  
    street = db.StringProperty(default='')
    street_no = db.StringProperty(default='')
    city = db.StringProperty(default='')
    post_code = db.StringProperty(default='')
    comment = db.StringProperty(default='')


    @staticmethod
    def list():
        return Student.all().filter('hidden',False).order('reg_datetime')
    
    @staticmethod
    def list_for_course(course_key):
        return Student.all().filter('hidden',False).filter('course_key',course_key).order('reg_datetime')


    def course_code(self):
        k = Student.course_key.get_value_for_datastore(self)
        return Course.get_code_by_key(k)

    def addressing_loc(self):
        if self.addressing == '-':
            return ''
        elif self.addressing == 'p':
            return 'Pan'
        elif self.addressing == 's':
            return 'Slečna'
        elif self.addressing == 'd':
            return 'Paní'
        return '?'

    def status_loc(self):
        if self.status == '-':
            return ''
        elif self.status == 'n':
            return 'nový' 
        elif self.status == 'nc':
            return 'platný nový'
        return '?' 
 

