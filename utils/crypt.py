# -*- coding: utf-8 -*-

from string import Template
from utils import config

import random
import logging
import string


def maketrans(i,o):
    t = dict((ord(a),unicode(b)) for (a,b) in zip(i,o) )
    return t

def transtab():
    it = unicode(config.getConfigString("CRYPTO_TABLE_I",'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    ot = unicode(config.getConfigString("CRYPTO_TABLE_O",'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    return maketrans(it,ot)    

def transtab_r():
    it = unicode(config.getConfigString("CRYPTO_TABLE_I",'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    ot = unicode(config.getConfigString("CRYPTO_TABLE_O",'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    return maketrans(ot,it)    


def _crypt(t):
    t = unicode(t)
    ct = t.translate(transtab())
    logging.info("_crypt %s %s"%(t,ct))
    return ct

def _decrypt(t):
    t = unicode(t)
    dt = t.translate(transtab_r())
    logging.info("_decrypt %s %s"%(t,dt))
    return dt


def _zip(s1,s2):
    return "".join(i for j in zip(s1,s2) for i in j)

def _expand(t,l,c):
    if len(t)>=l:
        return t
    return c*(l-len(t))+t
     

def _encode(id,key):
    if len(id)<len(key):
        id = _expand(id,len(key),'.')
    v = _crypt(_zip(id,key).replace('.',''))
    return v  

def _extract(t,cl):
    return "".join(c for c in t if c in cl)  

def _genkey(l):
    word = ''
    for i in range(l):   
        word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return word



def gen_key():
    return _genkey(16)

def encode_id_short(id,key):
    id = "%d"%id
    l = len(id)
    if l<4:
        l = 4
    return _encode(id,key[:l])

def encode_id_long(id,key):
    id = "%d"%id
    l = len(id)
    if l<8:
        l = 8
    return _encode(id,key[:l])
    

def decode_id(d):
    d = unicode(d)
    d = _decrypt(d)
    d = _extract(d,'0123456789')
    return d

