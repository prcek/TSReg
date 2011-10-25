# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from utils.data import UnicodeReader
from utils.mail import valid_email
from enroll.models import Course,Student,Season
from admin.models import FileBlob
from google.appengine.api import taskqueue

import logging
import cStringIO
import datetime
from utils.locale import local_timezone



def index(request):

    return render_to_response('admin/help_index.html', RequestContext(request, { }))

