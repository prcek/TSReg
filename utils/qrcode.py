# -*- coding: utf-8 -*-


import logging
import datetime
import base64
import zlib
from django.utils import simplejson as json

from enroll.models import Student,Course,Season
from utils import config as cfg
from cdbsync import DateTimeEncoder


def calc_qrcode_for_student(student,course,season):
	logging.info("calc qrcode for student %s"%student)
	q = dict()
	q["ver"] = "TS1"
	q["id"] = student.ref_gid
	q["season"] = season.public_name
	q["course"] = course.code
	q["name"] = student.name
	q["surname"] = student.surname
	q["sex"] = student.get_sex()	
 	logging.info("dict %s" % q)
	q_json = json.dumps(q,cls=DateTimeEncoder)
	logging.info(q_json)
	
	q_b64 = base64.b64encode(zlib.compress(q_json.encode("utf8")))
	check = "%s*%d" %(q_b64,student.ref_gid_salt)
	check2 = "%s*%s" %(q_b64,"TS")
	crc = zlib.crc32(check)
	crc2 = zlib.crc32(check2)
	logging.info("raw q_b64: %s"%(q_b64))
	logging.info("salt:%d crc32:%d crc32_2:%d"%(student.ref_gid_salt,crc,crc2))
	qcode = "TS*%d*%s*%d*%d**" % (student.ref_gid,q_b64,crc &0xffffffff,crc2 &0xffffffff)
	logging.info(qcode)
	return qcode

def calc_qrcode_for_cmdcard(course,cmd_id):
	q = dict()
	q["ver"] = "TS1"
	q["id"] = cmd_id
	q["course_id"] = str(course.key())
	q["course_code"] = course.code
	q["course_name"] = course.name
 	logging.info("dict %s" % q)
	q_json = json.dumps(q,cls=DateTimeEncoder)
	logging.info(q_json)
	q_b64 = base64.b64encode(zlib.compress(q_json.encode("utf8")))
	check = "%s*%s" %(q_b64,"TS_CMD")
	crc = zlib.crc32(check)
	qcode = "TS_CMD*%s*%d**" % (q_b64,crc &0xffffffff)
	return qcode



