# -*- coding: utf-8 -*-


from google.appengine.api import memcache

from utils import config
from string import Template
import logging
import re

NAMESPACE="ns1"

def get(key):
    v = memcache.get(key,namespace=NAMESPACE) 
    logging.info('cache.get %s %s'%(key,v))
    return v

def set(key,value,time=0):
    r=memcache.set(key,value,time,namespace=NAMESPACE)
    logging.info('cache.set %s %s %s %s'%(key,value,time,r))
    return r

def flush_all():
    r = memcache.flush_all()
    logging.info('cache.flush_all %s'%(r))
    return r

def delete(key):
    r = memcache.delete(key,namespace=NAMESPACE) 
    logging.info('cache.delete %s %s'%(key,r))
    return r


