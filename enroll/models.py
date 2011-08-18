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
    group_mode = db.StringProperty(choices=['Single','Pair'], default='Single')
    capacity = db.IntegerProperty(default=0)
    usage = db.IntegerProperty(default=0)
    pending = db.IntegerProperty(default=0)
    pending_limit = db.IntegerProperty(default=0)
    hidden = db.BooleanProperty(default=False)
    

    @staticmethod
    def list():
        return Course.all().filter('hidden',False).order('order_value').order('code')



