# -*- coding: utf-8 -*-


import logging
import datetime
import base64

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
	q_b64 = base64.urlsafe_b64encode(q_json)
	logging.info(q_b64)
	return q_b64
