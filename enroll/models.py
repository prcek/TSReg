# -*- coding: utf-8 -*-

from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging
import random

from utils import crypt

from string import maketrans

intab = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
outtab = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
transtab = maketrans(intab, outtab)
transtab_r = maketrans(outtab,intab)


class Course(BaseModel):
    active = db.BooleanProperty(default=False)
    suspend = db.BooleanProperty(default=False)
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
    

    def is_open(self):
        return (not self.hidden) and self.active and (not self.suspend)

    @staticmethod
    def list():
        return Course.all().filter('hidden',False).order('order_value').order('code')

    @staticmethod
    def list_for_enroll():
        return Course.all().filter('hidden',False).filter('active',True).order('order_value').order('code')


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
            res.append((c.key().__str__(),c.code))
        logging.info('get_COURSE_CHOICES: %s'%res)
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
    status = db.StringProperty(choices=['-','n','nc','e','k'], default='-')
    reg_by_admin = db.BooleanProperty(default=False)
    reg_datetime = db.DateTimeProperty()
    ref_base = db.StringProperty(default='')
    ref_key = db.StringProperty(default='')
    confirm_key = db.StringProperty(default='')
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

    def init_reg(self):
        self.reg_datetime = datetime.datetime.utcnow()        

    def init_ref_base(self):
        self.ref_base = crypt.gen_key()


    def init_ref_codes(self):
        id = self.key().id()
        self.ref_key = crypt.encode_id_short(id,self.ref_base)
        self.confirm_key = crypt.encode_id_long(id,self.ref_base)
        logging.info("id: %s, rk: %s, ck: %s"%(id,self.ref_key, self.confirm_key))
#        s2 = self.key().id().__str__()
#        if(len(s2)<4):
#            s2="."*(4-len(s2))+s2
#
#        s4 = self.key().id().__str__()
#        if(len(s4)<8):
#            s4="."*(8-len(s4))+s4
#
#
#        s1 = self.ref_base[:len(s2)]
#        s3 = self.ref_base[8:]
#        self.ref_key= "".join(i for j in zip(s1,s2) for i in j).translate(transtab,'.')
#        self.confirm_key = "".join(i for j in zip(s3,s4) for i in j).translate(transtab,'.')
#
#        logging.info("id:%s bk:%s s1:%s s2:%s s3:%s s4:%s ck:%s rk:%s"%(self.key().id(),self.ref_base,s1,s2,s3,s4,self.confirm_key,  self.ref_key))

    @staticmethod
    def decode_ref_key(r):
        i = crypt.decode_id(r) 
        id = None
        try:
            id = int(i)
        except:
            pass
        logging.info("r: %s, i: %s, id: %s"%(r,i,id))
        return id

#        r = r.__str__()
#        id = None
#        try:
##            r2 =  r.translate(transtab_r)
#            ids = r2.translate(None,'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
#            logging.info('r:%s k2:%s ids:%s'%(r,r2,ids))
#            id = int(ids)
#        except:
#            pass
#        return id
#"""

    @staticmethod
    def decode_confirm_key(r):
        i = crypt.decode_id(r) 
        id = None
        try:
            id = int(i)
        except:
            pass
        logging.info("r: %s, i: %s, id: %s"%(r,i,id))
        return id

#"""
#        r = r.__str__()
#        id = None
#        try:
#            r2 =  r.translate(transtab_r)
#            ids = r2.translate(None,'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
#            logging.info('r:%s k2:%s ids:%s'%(r,r2,ids))
#            id = int(ids)
#        except:
#            pass
#        return id
#"""

#r:R590I k2:HVZQ8 ids:8
#id:8 bk:HVZQDEYUIWSOKTSS s1:HVZQ s2:...8 s3:.......8 s4:IWSOKTSS ck:S62YU32I2 rk:R590I


    @staticmethod
    def get_by_ref_key(rk):
        logging.info('ref_key: %s'%rk)
        id = Student.decode_ref_key(rk)
        logging.info('id: %s'%id)
        if id is None:
            return None
        s = Student.get_by_id(id)
        if s is None:
            return None
        if s.ref_key != rk:
            return None
        return s

    @staticmethod
    def get_by_confirm_key(ck):
        logging.info('confirm_key: %s'%ck)
        id = Student.decode_confirm_key(ck)
        logging.info('id: %s'%id)
        if id is None:
            return None
        s = Student.get_by_id(id)
        if s is None:
            return None
        if s.confirm_key != ck:
            return None
        return s



    @staticmethod
    def list():
        return Student.all().filter('hidden',False).order('reg_datetime')


    @staticmethod
    def list_by_surname(s):
        return Student.all().filter('hidden',False).filter('surname',s).order('-reg_datetime')

    @staticmethod
    def list_by_email(e):
        return Student.all().filter('hidden',False).filter('email',e).order('-reg_datetime')


    @staticmethod
    def list_for_cleanup(time_limit):
        return Student.all().filter('hidden',False).filter('status','n').filter('reg_datetime <',time_limit).order('reg_datetime')

    @staticmethod
    def list_for_course(course_key):
        return Student.all().filter('hidden',False).filter('course_key',course_key).order('reg_datetime')

    @staticmethod
    def list_for_course_to_enroll(course_key):
        return Student.all().filter('hidden',False).filter('course_key',course_key).filter('status','nc').order('reg_datetime')

    @staticmethod
    def list_for_course_enrolled(course_key):
        return Student.all().filter('hidden',False).filter('course_key',course_key).filter('status','e').order('reg_datetime')





    def course_code(self):
        k = Student.course_key.get_value_for_datastore(self)
        return Course.get_code_by_key(k)

    def get_course(self):
        k = Student.course_key.get_value_for_datastore(self)
        return Course.get(k)

       

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
        elif self.status == 'e':
            return 'zapsán'
        elif self.status == 'k':
            return 'vyřazen'
        return '?' 
 

