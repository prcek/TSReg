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

    def group_mode_loc(self):
        if self.group_mode == 'Single':
            return 'jednotlivci'
        elif self.group_mode == 'Pair':
            return 'po párech'
        return '?'

class Student(BaseModel):
    hidden = db.BooleanProperty(default=False)
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



    def addressing_loc(self):
        if self.addressing == '-':
            return ''
        elif self.addressing == 'p':
            return 'Pán'
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
 

