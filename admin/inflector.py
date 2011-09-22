# -*- coding: utf-8 -*-

from admin.models import Inflect
import utils.config as cfg
import logging

class InflectDict:
    def __init__(self):
        self.data=dict()
    
    def add(self, pattern, value):
        self.data[pattern]=value 

    def find(self, pattern):
        if pattern in self.data:
            return self.data[pattern]
        return None
#    def __str__(self):
#        return self.data.__str__()
   
DICTS=None

def init_dicts():
    global DICTS
    logging.info('init dicts')
    inflect_list = Inflect.list()
    DICTS=dict()
    for i in inflect_list:
        dict_key = "%s_%s"%(i.gender,i.part)
        if not dict_key in DICTS:
            DICTS[dict_key]=InflectDict()
        DICTS[dict_key].add(i.pattern,i)


def flush_dicts():
    global DICTS
    logging.info('flush dicts')
    DICTS=None

def do_inflect(part,gender,text):
    global DICTS
    if DICTS is None:
        init_dicts()

    dict_key = "%s_%s"%(gender,part)
    logging.info('dict_key=%s, text=%s'%(dict_key,text))
    proposal = None
    if dict_key in DICTS:
        res = DICTS[dict_key].find(text) 
        if not res is None:
            logging.info('use pattern: %s'%res)
            proposal= res.proposal
        else:
            logging.info('no pattern match!')
    else:
        logging.info('no dict!')
    
    if proposal is None:
        proposal  = text 
    logging.info('proposal=%s'%proposal) 
    return proposal
