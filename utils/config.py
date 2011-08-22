# -*- coding: utf-8 -*-
from appengine_django.models import BaseModel
from google.appengine.ext import db
from django import forms
import logging


class Config(BaseModel):
    active = db.BooleanProperty()
    name = db.StringProperty()
    value = db.StringProperty()
    def as_csv_row(self):
        return [self.key().kind(),self.key().id(),self.active,self.name,self.value]
    def from_csv_row(self,row=[]):
        self.name = row[2]
        return True

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ( 'active', 'name','value' )

 
def getConfigString(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        logging.info('Config: %s=%s'%(name,c.value))
        return str(c.value)
    return dv 

def getConfigBool(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        logging.info('Config: %s=%s'%(name,c.value))
        if c.value=='1':
            return True
        else:
            return False
    
    return dv

def getConfigInt(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        logging.info('Config: %s=%s'%(name,c.value))
        try:
            return int(c.value)
        except:
            logging.info('Config: no Integer value!')
            return dv
    
    return dv

def getConfigList():
    return Config.objects.all().order('name')

def createConfig(name,value):
    c = Config.objects.all().filter('name =',name).get()
    if c is None:
        c = Config()
        c.name = name
        c.value = value
        c.active = False 
        c.save()

def setupConfig():
#    createConfig('REPORT_DAILY_SUMMARY','0')    
#    createConfig('REPORT_DAILY_TRANSACTIONS','0')
#    createConfig('PDF_TEST_TEXT',u'Příliš žluťoučký kůň úpěl ďábelské ódy (.CZ?!)')
#    createConfig('CLEARANCE_ALL_ORDER_ITEMS','0')
#    createConfig('ADMIN_EMAIL','admin@domain.com') 
#    createConfig('DEFAULT_SENDER','sender@domain.com')
#    createConfig('MAIL_SPLIT_COUNT','10')
#    createConfig('MAIL_TEST_TO','user@domain.com') 
#    createConfig('MAIL_TEST_FROM','admin@domain.com') 
#    createConfig('MAIL_TEST','0') 
#    createConfig('ENABLE_MAIL_JOBS','0')
#    createConfig('ENABLE_MAIL_TEST','0')
    createConfig('CAPTCHA_PUBLIC_KEY','1234567890')
    createConfig('CAPTCHA_PRIVATE_KEY','1234567890')
    createConfig('CAPTCHA_ON','1')
    
