# -*- coding: utf-8 -*-

from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging
import random

from utils import crypt
from utils import cache

from string import maketrans

#intab = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#outtab = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
#transtab = maketrans(intab, outtab)
#transtab_r = maketrans(outtab,intab)

def Bool2AnoNe(b):
    if b:
        return "Ano"
    else:
        return "Ne"


class Season(BaseModel):
    name = db.StringProperty(default='')
    public_name = db.StringProperty(default='')
    order_value = db.IntegerProperty(default=0)

    @staticmethod
    def get_name_by_key(season_key):
        return season_key_2_name(season_key)

    @staticmethod
    def list():
        return get_season_list()


    @staticmethod
    def get_SEASON_CHOICES():
        clist = get_season_list()
        res = []
        for c in clist:
            res.append((c.key().__str__(),c.name))
#        logging.info('get_SEASON_CHOICES: %s'%res)
        return res 


    def get_COURSE_CHOICES(self):
        clist = Course.list_season(str(self.key()))
        res = []
        for c in clist:
            res.append((c.key().__str__(),c.code))
 #       logging.info('season.get_COURSE_CHOICES: %s'%res)
        return res




class Folder(BaseModel):
    name = db.StringProperty(default='')
    public_name = db.StringProperty(default='')
    order_value = db.IntegerProperty(default=0)

    @staticmethod
    def get_name_by_key(folder_key):
        return folder_key_2_name(folder_key)

    @staticmethod
    def list():
        return get_folder_list()

    @staticmethod
    def get_FOLDER_CHOICES():
        clist = get_folder_list()
        res = []
        for c in clist:
            res.append((c.key().__str__(),c.name))
#        logging.info('get_FOLDER_CHOICES: %s'%res)
        return res 






class Course(BaseModel):
    active = db.BooleanProperty(default=False)
    suspend = db.BooleanProperty(default=False)
    folder_key = db.StringProperty()
    season_key = db.StringProperty()
    code = db.StringProperty(default='')
    name = db.StringProperty(default='')
    order_value = db.IntegerProperty(default=0)
    period = db.StringProperty(default='')
    first_period = db.StringProperty(default='')
    place = db.StringProperty(default='')
    teacher = db.StringProperty(default='')
    cost_a = db.IntegerProperty(default=0)
    cost_b = db.IntegerProperty(default=0)
    cost_sa = db.IntegerProperty(default=0)
    cost_sb = db.IntegerProperty(default=0)
    group_mode = db.StringProperty(choices=['Single','Pair','School'], default='Single')
    cost_mode = db.StringProperty(choices=['Normal','Period','Fix'], default='Normal')
    cost_sale = db.BooleanProperty(default=False)
    capacity = db.IntegerProperty(default=0)
    usage = db.IntegerProperty(default=0)
    pending_payment = db.IntegerProperty(default=0)
    pending = db.IntegerProperty(default=0)
    pending_limit = db.IntegerProperty(default=0)
    stat_e_m =  db.IntegerProperty(default=0)
    stat_s_m =  db.IntegerProperty(default=0)
    stat_e_f =  db.IntegerProperty(default=0)
    stat_s_f =  db.IntegerProperty(default=0)
    stat_e_p =  db.IntegerProperty(default=0)
    stat_s_p =  db.IntegerProperty(default=0)
    hidden = db.BooleanProperty(default=False)
    card_line_1 = db.StringProperty(default='')
    card_line_2 = db.StringProperty(default='')
    modify_datetime = db.DateTimeProperty()
    backup_datetime = db.DateTimeProperty()
    backup_flag = db.BooleanProperty(default=False)

    def folder_name(self):
        return Folder.get_name_by_key(self.folder_key)

    def get_folder(self):
        return Folder.get(self.folder_key)

    def season_name(self):
        return Season.get_name_by_key(self.season_key)

    def get_season(self):
        return Season.get(self.season_key)



    def is_open(self):
        return (not self.hidden) and self.active and (not self.suspend)

    @staticmethod
    def list():
        return Course.all().filter('hidden',False).order('order_value').order('code')

    @staticmethod
    def list_filter(season_key,folder_key):
        return Course.all().filter('hidden',False).filter('season_key',season_key).filter('folder_key',folder_key).order('order_value').order('code')

    @staticmethod
    def list_season(season_key):
        return Course.all().filter('hidden',False).filter('season_key',season_key).order('order_value').order('code')
        

    @staticmethod
    def list_for_enroll():
        return Course.all().filter('hidden',False).filter('active',True).order('order_value').order('code')

    @staticmethod
    def list_for_backup_check(time_limit):
        return Course.all().filter('hidden',False).filter('modify_datetime >',time_limit).filter('backup_flag',False)

    @staticmethod
    def list_for_backup():
        return Course.all().filter('hidden',False).filter('backup_flag',True)


    @staticmethod
    def get_code_by_key(course_key):
        if course_key is None:
            return None
        c = Course.get(course_key)
        if c is None:
            return None
        return c.code

    @staticmethod
    def get_season_by_key(course_key):
        if course_key is None:
            return None
        c = Course.get(course_key)
        if c is None:
            return None
        return c.season_name()



    @staticmethod
    def get_COURSE_CHOICES():
        clist = Course.list()
        res = []
        for c in clist:
            res.append((c.key().__str__(),c.code))
#        logging.info('get_COURSE_CHOICES: %s'%res)
        return res 


    def can_enroll(self):
        return (self.usage<self.capacity)

    def only_pair_enroll(self):
        return (self.group_mode == 'Pair')

    def group_mode_loc(self):
        if self.group_mode == 'Single':
            return 'jednotlivci'
        elif self.group_mode == 'Pair':
            return 'po párech'
        elif self.group_mode == 'School':
            return 'po třídách'
        return '?'

    def cost_mode_loc(self):
        if self.cost_mode == 'Normal':
            return 'N'
        elif self.cost_mode == 'Period':
            return 'P'
        elif self.cost_mode == 'Fix':
            return 'F'
        return '?'

    def mark_as_modify(self):
        self.modify_datetime = datetime.datetime.utcnow()        

    def mark_as_backup(self):
        self.backup_datetime = datetime.datetime.utcnow()        
        self.backup_flag = False 

    


class Student(BaseModel):
    hidden = db.BooleanProperty(default=False)
    course_key = db.StringProperty()
    status = db.StringProperty(choices=['-','n','s','e','k'], default='-')
    reg_by_admin = db.BooleanProperty(default=False)
    reg_datetime = db.DateTimeProperty()
    enroll_datetime = db.DateTimeProperty()
    ref_base = db.StringProperty(default='')
    ref_key = db.StringProperty(default='')
    confirm_key = db.StringProperty()
    addressing = db.StringProperty(choices=['-','p','s','d'], default='-')
    name = db.StringProperty(default='')
    surname = db.StringProperty(default='')
    student = db.BooleanProperty(default=False)
    student_check = db.BooleanProperty(default=False)
    long_period = db.BooleanProperty(default=False)
    to_pay = db.IntegerProperty(default=0)
    balance_due = db.IntegerProperty(default=0)
    discount = db.StringProperty(default='')
    paid_ok = db.BooleanProperty(default=False)
    year = db.IntegerProperty(default=0)
    email = db.StringProperty(default='') 
    no_email_notification = db.BooleanProperty(default=False)
    no_email_info = db.BooleanProperty(default=False)
    no_email_ad = db.BooleanProperty(default=False)
    phone = db.StringProperty(default='')  
    street = db.StringProperty(default='')
    street_no = db.StringProperty(default='')
    city = db.StringProperty(default='')
    post_code = db.StringProperty(default='')
    partner_ref_code = db.StringProperty(default='')
    school = db.StringProperty(default='')
    school_class = db.StringProperty(default='')
    comment = db.StringProperty(default='')
    modify_datetime = db.DateTimeProperty()

    x_pair_empty_slot = False
    x_pair_no = 0
    x_pair_complete = False
    x_pair_first = False
    x_pair_second = False

    x_no = 0
    x_class_no = 0

    x_import_no_1 = None
    x_import_no_2 = None


    def clone(self):
        s = Student() 
        s.init_reg()
        s.init_ref_base()
        s.init_enroll()
        s.course_key = self.course_key
        s.status = self.status
        s.reg_by_admin = True
        s.addressing = self.addressing 
        s.name = self.name
        s.surname = self.surname

        s.student  = self.student
#        s.student_check = self.student_check
#        s.long_period 
#        s.to_pay 
#        s.balance_due
#        s.discount
#        s.paid_ok 
        s.year = self.year
        s.email = self.email
        s.no_email_notification = self.no_email_notification
        s.no_email_info = self.no_email_info
        s.no_email_ad = self.no_email_ad
        s.phone = self.phone
        s.street  = self.street
        s.street_no  = self.street_no
        s.city = self.city
        s.post_code  = self.post_code
        s.partner_ref_code  = self.partner_ref_code
        s.school = self.school
        s.school_class = self.school_class
        s.comment = self.comment


        s.save()
        s.init_ref_codes();
        s.save()

        return s

    def init_reg(self):
        self.reg_datetime = datetime.datetime.utcnow()        

    def init_enroll(self):
        self.enroll_datetime = datetime.datetime.utcnow()        

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
        if s.hidden:
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
        if s.hidden:
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
    def list_by_partner(p):
        return Student.all().filter('hidden',False).filter('partner_ref_code',p)

    @staticmethod
    def list_for_cleanup(time_limit):
        return Student.all().filter('hidden',False).filter('status','n').filter('reg_datetime <',time_limit).order('reg_datetime')


    @staticmethod
    def list_for_course(course_key):
        return Student.all().filter('hidden',False).filter('course_key',str(course_key)).order('reg_datetime')

    @staticmethod
    def list_for_course_to_enroll(course_key):
        return Student.all().filter('hidden',False).filter('course_key',str(course_key)).filter('status','s').order('reg_datetime')

    @staticmethod
    def list_for_course_enrolled(course_key):
        return Student.all().filter('hidden',False).filter('course_key',str(course_key)).filter('status','e').order('reg_datetime')



    
    def course_code(self):
        return Course.get_code_by_key(self.course_key)

    def course_season(self):
        return Course.get_season_by_key(self.course_key)

    def get_course(self):
        return Course.get(self.course_key)

    def get_course_id(self):
        c =  Course.get(self.course_key)
        if c is None:
            return None
        return c.key().id()

    def set_course_key(self,course_key):
        self.course_key = course_key
        
        
        
    def get_sex(self):
        if self.addressing == 'p':
            return 'm'
        elif self.addressing == 's':
            return 'f'
        elif self.addressing == 'd':
            return 'f'
        else:
            return '-'
    

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
            return 'podaná' 
        elif self.status == 's':
            return 'náhradník'
        elif self.status == 'e':
            return 'zapsán'
        elif self.status == 'k':
            return 'vyřazen'
        return '?' 

 
    def mark_as_modify(self):
        self.modify_datetime = datetime.datetime.utcnow()        


    def as_csv_row(self):
        if (self.x_no!=0):
            no1 = self.x_no
        else:
            no1 = ''
       
        if (self.x_pair_no!=0):
            no2 = self.x_pair_no
        elif (self.x_class_no!=0):
            no2 = self.x_class_no
        else:
            no2 = ''
 
        if self.addressing == '-':
            addressing=''
        else:
            addressing=self.addressing
 
        return [
            no1,no2,addressing,self.surname,self.name, self.to_pay, self.balance_due, self.discount,
            self.school,self.school_class, self.street, self.street_no, self.city, self.post_code, self.phone,
            self.email, Bool2AnoNe(not self.no_email_ad), Bool2AnoNe(self.student), Bool2AnoNe(self.student_check),
            self.comment,
            self.status, Bool2AnoNe(self.reg_by_admin), self.reg_datetime, self.enroll_datetime, self.ref_base, self.ref_key, self.confirm_key,
            Bool2AnoNe(self.long_period), Bool2AnoNe(self.paid_ok), self.year, Bool2AnoNe(self.no_email_info), Bool2AnoNe(self.no_email_notification), self.partner_ref_code, self.modify_datetime
        ]





def build_season_dict():
    q = Season.all()
    d=dict()
    for s in q:
        d[str(s.key())]=s
    return d

def build_season_list():
    q = Season.all().order('order_value').order('name')
    d=[]
    for s in q:
        d.append(s)
    return d



def get_season_dict():
    d = cache.get('season_dict')
    if d is None:
        d = build_season_dict()
        cache.set('season_dict',d)
    return d

def get_season_list():
    d = cache.get('season_list')
    if d is None:
        d = build_season_list()
        cache.set('season_list',d)
    return d



def build_folder_dict():
    q = Folder.all()
    d=dict()
    for f in q:
        d[str(f.key())]=f
    return d

def build_folder_list():
    q = Folder.all().order('order_value').order('name')
    d=[]
    for f in q:
        d.append(f)
    return d

def get_folder_dict():
    d = cache.get('folder_dict')
    if d is None:
        d = build_folder_dict()
        cache.set('folder_dict',d)
    return d

def get_folder_list():
    d = cache.get('folder_list')
    if d is None:
        d = build_folder_list()
        cache.set('folder_list',d)
    return d


def rebuild_seasons():
    cache.delete('season_dict')    
    cache.delete('season_list')    
    
def rebuild_folders():
    cache.delete('folder_dict')    
    cache.delete('folder_list')    

def season_key_2_name(season_key):
    s=get_season_dict().get(season_key)
    if s is None:
        return None
    return s.name

def folder_key_2_name(folder_key):
    f=get_folder_dict().get(folder_key)
    if f is None:
        return None
    return f.name

