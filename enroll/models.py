from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging

class Course(BaseModel):
    code = db.StringProperty(default='')
    name = db.StringProperty(default='')
    category = db.StringProperty(default='')
    group_mode = db.StringProperty(choices=['Single','Pair'], default='Single')
    hidden = db.BooleanProperty(default=False)
    



