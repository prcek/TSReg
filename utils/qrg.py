# -*- coding: utf-8 -*-


import logging
import datetime
import base64

from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.api.urlfetch import Fetch,POST
from google.appengine.api import taskqueue

from cdbsync import DateTimeEncoder 
from enroll.models import Course,Folder,Season,Student
from utils import config as cfg

#CDB_URL="https://cdb.hluchan.cz/test/"

#CDB_AUTH=base64.b64encode("admin:password")

QRG_VALIDATE_CERT = True


def qrg_cfg_get_url():
	return cfg.getConfigString("QRG_URL","<missing QRG_URL cfg value>")

def qrg_cfg_get_auth():
	return cfg.getConfigString("QRG_AUTH","<missing QRG_AUTH cfg value>")

def qrg_cfg_get_on():
	return cfg.getConfigBool("QRG_ON",False)


def qrg_get_info():
	logging.info("qrg info - %s"%(qrg_cfg_get_url()))

	res = Fetch("%s/" % (qrg_cfg_get_url()),headers={"Authorization": "Basic %s" % qrg_cfg_get_auth()},validate_certificate=QRG_VALIDATE_CERT)
	logging.info("qrg get http res code %d", res.status_code) 
	if res.status_code == 200:
		logging.info(res.content)
		info = json.loads(res.content)
		logging.info(info)
		return info
	return "%s %s" % (res.status_code,res.content)


def qrg_post(srv,data):
	logging.info("qrg post %s"%srv)
	post_json = json.dumps(data,cls=DateTimeEncoder)
	logging.info("qrg post json %s"%post_json)
	res = Fetch("%s/%s" % (qrg_cfg_get_url(),srv),deadline=60,method=POST,payload=post_json, headers={"Authorization": "Basic %s" % qrg_cfg_get_auth(), "Content-Type":"application/json"},validate_certificate=QRG_VALIDATE_CERT)
	logging.info("qrg post http res code %d", res.status_code)
	logging.info(res.content)
	if res.status_code == 200:
		doc = json.loads(res.content)
		return doc
	logging.info("status <> 200, return None")
	return None


