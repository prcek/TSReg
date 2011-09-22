# -*- coding: utf-8 -*-

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
 
