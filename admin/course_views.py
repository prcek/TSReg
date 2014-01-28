# -*- coding: utf-8 -*-

#from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Context, loader

from google.appengine.api import taskqueue
from google.appengine.ext import ndb


from wtforms.ext.appengine.db import model_form
from wtforms.form import Form
from wtforms.fields import SelectField, TextField
from utils.wtf  import DisabledTextField, InputRequired



from enroll.models import Course,Folder,Season
from utils.decorators import ar_edit
import utils.config as cfg
import logging


GROUP_MODE_CHOICES = (
    ('Single',u'jednotlivci'),
    ('Pair',u'po párech'),
    ('School',u'po třídách'),
)

COST_MODE_CHOICES = (
    ('Normal',u'dospělý/student'),
    ('Period',u'celo/polo-roční'),
    ('Fix',u'pevná'),
)



class CourseFormBase(Form):
    season_key = SelectField(label=u'sezóna',coerce=str)
    folder_key = SelectField(label=u'kategorie',coerce=str)

    def __init__(self,  *args, **kwargs):
        super(CourseFormBase,self).__init__(*args, **kwargs)
        self.season_key.choices = Season.get_SEASON_CHOICES()
        self.folder_key.choices = Folder.get_FOLDER_CHOICES()




CourseForm= model_form(Course, base_class=CourseFormBase, only=['active', 'order_value', 
                'code','name', 'period', 'first_period', 'place', 'teacher', 
                'cost_a', 'cost_b', 'cost_sa', 'cost_sb', 'cost_sale', 'cost_mode', 
                'group_mode', 'capacity', 'pending_limit','card_line_1','card_line_2'], field_args = {

        'active': { 'label':u'aktivní', 'description':u'je-li kurz aktivní, bude nabízen pro zápis'},
        'order_value': { 'label':u'řazení', 'description':u'kurzy budou tříděny podle tohodle čísla v zestupném pořadí', 'validators':[InputRequired()] },
        'code': { 'label': u'kód', 'validators':[InputRequired()] },
        'name': { 'label': u'název', 'validators':[InputRequired()] },
        'season_key': { 'label': u'sezóna', 'validators':[InputRequired()] },
        'folder_key': { 'label': u'kategorie', 'validators':[InputRequired()] },
        'period': { 'label': u'termín', 'validators':[InputRequired()] },
        'first_period': { 'label': u'zahájení', 'validators':[InputRequired()] },
        'place': { 'label': u'místo', 'validators':[InputRequired()] },
        'teacher': { 'label': u'lektor', 'validators':[InputRequired()] },
        'cost_a': { 'label': u'cena A', 'description': u'dospělý, celo-roční nebo pevná', 'validators':[InputRequired()] },
        'cost_b': { 'label': u'cena B', 'description': u'student, pololetní', 'validators':[InputRequired()] },
        'cost_sa': { 'label': u'cena SA', 'description': u'při aktivní slevě pro dospělý, celo-roční nebo pevná', 'validators':[InputRequired()] },
        'cost_sb': { 'label': u'cena SB', 'description': u'při aktivní slevě pro student, pololetní', 'validators':[InputRequired()] },
        'cost_mode': { 'label': u'režim ceny', 'validators':[InputRequired()], 'choices':COST_MODE_CHOICES },
        'cost_sale': { 'label': u'aktivní sleva' },
        'group_mode': { 'label': u'režim zápisu','validators':[InputRequired()], 'choices':GROUP_MODE_CHOICES },
        'capacity': { 'label': u'kapacita', 'validators':[InputRequired()]},
        'pending_limit': { 'label': u'náhradníci', 'validators':[InputRequired()]},
        'card_line_1': { 'label': u'tisk 1.ř.' },
        'card_line_2': { 'label': u'tisk 2.ř.' },
})




class SeasonCategoryFilterForm(Form):
    season_key = SelectField(label=u'sezóna',coerce=str)
    folder_key = SelectField(label=u'kategorie',coerce=str)

    def __init__(self,  *args, **kwargs):
        super(SeasonCategoryFilterForm,self).__init__(*args, **kwargs)
        self.season_key.choices = Season.get_SEASON_CHOICES()
        self.folder_key.choices = Folder.get_FOLDER_CHOICES()


def index(request):

    course_list =None
    season = None
    folder = None
    if request.method == 'POST':
        logging.info('setting new season/folder')
        form = SeasonCategoryFilterForm(request.POST)
        if form.validate():
            logging.info(form.data)
            season_key = ndb.Key(urlsafe=form.data['season_key'])
            season = season_key.get()
            #season = Season.get(form.data['season_key'])
            folder = Folder.get(form.data['folder_key'])
            logging.info('season %s' % season)
            logging.info('folder %s' % folder)
            if not season is None:
                request.session['course_season_key']=season.key.urlsafe()
            if not folder is None:
                request.session['course_folder_key']=str(folder.key())
    else:
        cskey = request.session['course_season_key']
        if not cskey is None:
            season_key = ndb.Key(urlsafe=cskey)
            season =  season_key.get()
        cfkey = request.session['course_folder_key']
        if not cfkey is None:
            folder =  Folder.get(str(cfkey))


        if (season is None) or (folder is None):
            form = SeasonCategoryFilterForm()
        else:
            form = SeasonCategoryFilterForm(season_key=season.key.urlsafe(), folder_key=str(folder.key()))

    if (season is None) or (folder is None):
        course_list = None
        if request.GET.get('all',None):
            logging.info('all mode')
            course_list=Course.list()
 
    else:
        if request.GET.get('all',None):
            logging.info('all mode')
            course_list=Course.list()
        else:
            course_list=Course.list_filter(season,str(folder.key()))

    return render_to_response('admin/courses_index.html', RequestContext(request, { 'form':form, 'course_list': course_list }))


@ar_edit
def edit(request, course_id):

    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    if request.method == 'POST':
        form = CourseForm(request.POST, obj=course)
        if form.validate():
            logging.info('edit course before %s'% course)
            form.populate_obj(course)
            logging.info('edit course after %s'% course)
            course.mark_as_modify()
            course.put()
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})
            return HttpResponseRedirect('../..')
    else:
        form = CourseForm(obj=course)

    return render_to_response('admin/courses_edit.html', RequestContext(request, {'form':form}))

@ar_edit
def create(request):

    course = Course()
    season = None
    folder = None
    cskey = request.session['course_season_key']
    if not cskey is None:
        season =  Season.get(str(cskey))
    cfkey = request.session['course_folder_key']
    if not cfkey is None:
        folder =  Folder.get(str(cfkey))

    if not( (folder is None) or (Season is None) ):
        course.folder_key = cfkey
        course.season_key = cskey



    if request.method == 'POST':
        form = CourseForm(request.POST, obj=course)
        if form.validate():
            logging.info('edit course before %s'% course)
            form.populate_obj(course)
            logging.info('edit course after %s'% course)
            course.mark_as_modify()
            course.put()
            return HttpResponseRedirect('..')
    else:
        form = CourseForm(obj=course)
    return render_to_response('admin/courses_create.html', RequestContext(request, {'form':form}))

def recount(request, course_id):

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})

    return HttpResponseRedirect("../..")


@ar_edit
def delete(request, course_id):

    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    taskqueue.add(url='/task/hide_course_students/', params={'course_id':course.key().id()})

    course.hidden = True
    course.mark_as_modify()
    course.put()

    return HttpResponseRedirect("../..")


    

