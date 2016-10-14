# -*- coding: utf-8 -*-


import logging
import datetime
import base64

from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.api.urlfetch import Fetch,PUT
from google.appengine.api import taskqueue


from enroll.models import Course,Folder,Season,Student,StudentInvCard
from utils import config as cfg

#CDB_URL="https://cdb.hluchan.cz/test/"

#CDB_AUTH=base64.b64encode("admin:password")

CDB_VALIDATE_CERT = True

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object


def cdb_cfg_get_url():
	return cfg.getConfigString("CDBSYNC_URL","<missing CDBSYNC_URL cfg value>")

def cdb_cfg_get_auth():
	return cfg.getConfigString("CDBSYNC_AUTH","<missing CDBSYNC_AUTH cfg value>")

def cdb_cfg_get_on():
	return cfg.getConfigBool("CDBSYNC_ON",False)


def cdb_get_db_info():
	logging.info("cdb get db info - %s"%(cdb_cfg_get_url()))

	res = Fetch("%s" % (cdb_cfg_get_url()),headers={"Authorization": "Basic %s" % cdb_cfg_get_auth()},validate_certificate=CDB_VALIDATE_CERT)
	logging.info("cdb get http res code %d", res.status_code) 
	if res.status_code == 200:
		logging.info(res.content)
		doc = json.loads(res.content)
		logging.info(doc)
		return doc
	return "%s %s" % (res.status_code,res.content)


def cdb_get(id):
	logging.info("cdb get id %s" % id)
	res = Fetch("%s/%s" % (cdb_cfg_get_url(),id),headers={"Authorization": "Basic %s" % cdb_cfg_get_auth()},validate_certificate=CDB_VALIDATE_CERT)
	logging.info("cdb get http res code %d", res.status_code) 
	if res.status_code == 200:
		logging.info(res.content)
		doc = json.loads(res.content)
		logging.info(doc)
		return doc
	return None

def cdb_put(id,doc):
	logging.info("cdb put id %s" % id)
	doc_json = json.dumps(doc,cls=DateTimeEncoder)
	logging.info("cdb put json doc %s"%doc_json)
	res = Fetch("%s/%s" % (cdb_cfg_get_url(),id),method=PUT,payload=doc_json, headers={"Authorization": "Basic %s" % cdb_cfg_get_auth()},validate_certificate=CDB_VALIDATE_CERT)
	logging.info("cdb put http res code %d", res.status_code)
	logging.info(res.content)
	if res.status_code == 201:
		doc = json.loads(res.content)
		return doc
	return None


def cdb_create_or_update(key):
	logging.info("object key=%s" % key)
	try:
		kkey = db.Key(key)
		logging.info("objet kind %s and id %s" % (kkey.kind(),kkey.id_or_name()))   
		#if kkey.kind() is "Season":
		#	obj = db.Model.get(kkey)
		#else:	
		obj = db.Model.get(kkey)
	except Exception, e:
		logging.warn("can't get from ds (%s)"%e)
		return
	logging.info(obj)
	doc = cdb_get(key)
	
	if doc is None:
		logging.info("cdb doc not found")
		doc=db.to_dict(obj)
		doc["gae_ds_kind"] = kkey.kind()
		doc["gae_ds_id"] = kkey.id_or_name()
		logging.info("creating new one")
		rdoc = cdb_put(key,doc)
		if rdoc is None:
			logging.error("can't create doc")
			raise Exception("can't create doc")
		else:
			logging.info("res = %s" % rdoc)
	else:
		logging.info("cdb doc found")
		doc=db.to_dict(obj,doc)
		logging.info("update")
		rdoc = cdb_put(key,doc)
		if rdoc is None:
			logging.error("can't update doc")
			raise Exception("can't update doc")
		else:
			logging.info("res = %s" % rdoc)
	

def planned_cdb_put(key):
	cdb_create_or_update(key)

def plan_cdb_put(model):
	if not cdb_cfg_get_on():
		logging.info("cdbsync is disabled")
		return
	key = str(model.key())
	taskqueue.add(queue_name='cdbsync', url='/task/cdbsync_model/', target='', params={'key':key, 'action':'put'})

