# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from utils.data import UnicodeReader
from utils.mail import valid_email
from enroll.models import Course,Student,Season
from admin.models import FileBlob,CourseBackup
from google.appengine.api import taskqueue
import urllib
import logging
import cStringIO
import datetime
from utils.locale import local_timezone


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


class SeasonField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Season.get_SEASON_CHOICES())
        return super(SeasonField,self).valid_value(value)

class SeasonFilterForm(forms.Form):
    season_key = SeasonField(label='sezóna', error_messages=ERROR_MESSAGES)
    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['season_key']._set_choices(Season.get_SEASON_CHOICES())
 

def index(request):

    season = None
    if request.method == 'POST':
        filter_form = SeasonFilterForm(request.POST)
        if filter_form.is_valid():
            season = Season.get(str(filter_form.cleaned_data['season_key']))
            if not season is None:
                request.session['backup_season_key']=str(season.key())
    else:
        bskey = request.session.get('backup_season_key',None)
        if not bskey is None:
            season =  Season.get(str(bskey))
        if season is None:
            filter_form = SeasonFilterForm()
        else:
            filter_form = SeasonFilterForm({'season_key':str(season.key())})



    if season is None:
        course_list = None
    else:
        course_list = Course.list_season(str(season.key())) 

    return render_to_response('admin/backup_index.html', RequestContext(request, { 'filter_form':filter_form, 'course_list': course_list}))

def plan_backup(request,course_id):

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    logging.info('course: %s'%course)
    taskqueue.add(url='/task/course_backup/', params={'course_id':course.key().id()})

    return HttpResponseRedirect('../..')

def index_course(request, course_id):
    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    logging.info('course: %s'%course)
    backup_list = CourseBackup.list_for_course(str(course.key()))
    
    return render_to_response('admin/backup_list.html', RequestContext(request, { 'backup_list': backup_list, 'course':course}))
   
def get_backup(request, course_id, course_backup_id):
    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    course_backup = CourseBackup.get_by_id(int(course_backup_id))
    if course_backup is None:
        raise Http404


    r =  HttpResponse(course_backup.data,mimetype='application/vnd.ms-excel')
    file_name = urllib.quote(course_backup.filename)
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    return r



