# -*- coding: utf-8 -*-

from admin.models import Inflect
import utils.config as cfg
import logging

class InflectDict:
    def __init__(self):
        self.root = [None, {}]

    def add(self, pattern, proposal):
        curr_node = self.root
        for ch in pattern[::-1]:
            curr_node = curr_node[1].setdefault(ch, [None, {}])
        curr_node[0] = (pattern,proposal)

    def find_max(self, key):
        curr_node = self.root
        prefix_len = 0
        for ch in key[::-1]:
            try:
                curr_node = curr_node[1][ch]
                prefix_len+=1
            except KeyError:
                if curr_node == self.root:
                    return (0,None)
                break

        while curr_node[0] is None:
            curr_node = curr_node[1].itervalues().next()
 
        return (prefix_len,curr_node[0])



    def inflect(self, text, default = None):
        (suffix_len, rule) = self.find_max(text)
        if suffix_len == 0:
            logging.info('no rule')
            return default 
        logging.info('suffix_len=%d, rule=%s'%(suffix_len,rule))

        pattern = rule[0]
        proposal = rule[1]

        if text == pattern:
            return proposal

        base = text[:-suffix_len]
        pattern_base = pattern[:-suffix_len]
        prefix_len = len(pattern_base) 
        proposal_suffix = proposal[prefix_len:]
        return base+proposal_suffix
        


   
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
        DICTS[dict_key].add(i.pattern,i.proposal)


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
        res = DICTS[dict_key].inflect(text) 
        if not res is None:
            logging.info('result: %s'%res)
            proposal = res
        else:
            logging.info('no pattern match!')
    else:
        logging.info('no dict!')
    
    if proposal is None:
        proposal  = text 
    logging.info('proposal=%s'%proposal) 
    return proposal
