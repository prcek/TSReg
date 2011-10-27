# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from google.appengine.api import taskqueue


from enroll.models import Course,Folder,Season
import utils.config as cfg
import logging


GROUP_MODE_CHOICES = (
    ('Single','jednotlivci'),
    ('Pair','po párech'),
    ('School','po třídách'),
)

COST_MODE_CHOICES = (
    ('Normal','student/dospělý'),
    ('Period','polo/celo-roční'),
    ('Fix','pevná'),
)


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}

class FolderField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Folder.get_FOLDER_CHOICES())
        return super(FolderField,self).valid_value(value)

class SeasonField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Season.get_SEASON_CHOICES())
        return super(SeasonField,self).valid_value(value)




class CourseForm(forms.ModelForm):
    active = forms.BooleanField(label='aktivní', required=False, help_text='je-li kurz aktivní, bude nabízen pro zápis')
    order_value = forms.IntegerField(label='řazení',error_messages=ERROR_MESSAGES, help_text='kurzy budou tříděny podle tohodle čísla v zestupném pořadí')
    code = forms.CharField(label='kód', error_messages=ERROR_MESSAGES)
    name = forms.CharField(label='název', error_messages=ERROR_MESSAGES)
    season_key = SeasonField(label='sezóna', error_messages=ERROR_MESSAGES)
    folder_key = FolderField(label='kategorie', error_messages=ERROR_MESSAGES)
    period = forms.CharField(label='termín', error_messages=ERROR_MESSAGES)
    first_period = forms.CharField(label='zahájení', error_messages=ERROR_MESSAGES)
    place = forms.CharField(label='místo', error_messages=ERROR_MESSAGES)
    teacher = forms.CharField(label='lektor', error_messages=ERROR_MESSAGES)
    cost_a = forms.IntegerField(label='cena A', error_messages=ERROR_MESSAGES)
    cost_b = forms.IntegerField(label='cena B', error_messages=ERROR_MESSAGES)
    cost_sa = forms.IntegerField(label='cena SA', error_messages=ERROR_MESSAGES)
    cost_sb = forms.IntegerField(label='cena SB', error_messages=ERROR_MESSAGES)
    cost_mode = forms.CharField(label='režim ceny', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=COST_MODE_CHOICES)) 
    cost_sale = forms.BooleanField(label='aktivní sleva', required=False)
    group_mode = forms.CharField(label='režim zápisu', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=GROUP_MODE_CHOICES)) 
    capacity = forms.IntegerField(label='kapacita', error_messages=ERROR_MESSAGES)
    pending_limit = forms.IntegerField(label='náhradníci', error_messages=ERROR_MESSAGES)
    card_line_1 = forms.CharField(label='tisk 1.ř.', error_messages=ERROR_MESSAGES, required=False)
    card_line_2 = forms.CharField(label='tisk 2.ř.', error_messages=ERROR_MESSAGES, required=False)


    class Meta:
        model = Course
        fields = ( 'folder_key','season_key', 'active', 'order_value', 'code','name', 'period', 'first_period', 'place', 'teacher', 
                'cost_a', 'cost_b', 'cost_sa', 'cost_sb', 'cost_sale', 'cost_mode', 'group_mode', 'capacity', 'pending_limit','card_line_1','card_line_2' )

    def clean_code(self):
        data = self.cleaned_data['code']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data

    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['folder_key']._set_choices(Folder.get_FOLDER_CHOICES())
        self.fields['season_key']._set_choices(Season.get_SEASON_CHOICES())



class SeasonCategoryFilterForm(forms.Form):
    season_key = SeasonField(label='sezóna', error_messages=ERROR_MESSAGES)
    folder_key = FolderField(label='kategorie', error_messages=ERROR_MESSAGES)
    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['folder_key']._set_choices(Folder.get_FOLDER_CHOICES())
        self.fields['season_key']._set_choices(Season.get_SEASON_CHOICES())
    


def index(request):

    course_list =None
    season = None
    folder = None
    if request.method == 'POST':
        form = SeasonCategoryFilterForm(request.POST)
        if form.is_valid():
            season = Season.get(str(form.cleaned_data['season_key']))
            folder = Folder.get(str(form.cleaned_data['folder_key']))
            if not season is None:
                request.session['course_season_key']=str(season.key())
            if not folder is None:
                request.session['course_folder_key']=str(folder.key())
    else:
        cskey = request.session.get('course_season_key',None)
        if not cskey is None:
            season =  Season.get(str(cskey))
        cfkey = request.session.get('course_folder_key',None)
        if not cfkey is None:
            folder =  Folder.get(str(cfkey))


        if (season is None) or (folder is None):
            form = SeasonCategoryFilterForm()
        else:
            form = SeasonCategoryFilterForm({'season_key':str(season.key()), 'folder_key':str(folder.key())})

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
            course_list=Course.list_filter(str(season.key()),str(folder.key()))

    return render_to_response('admin/courses_index.html', RequestContext(request, { 'form':form, 'course_list': course_list }))



def edit(request, course_id):

    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.mark_as_modify()
            course.save()
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})
            return HttpResponseRedirect('../..')
    else:
        form = CourseForm(instance=course)

    return render_to_response('admin/courses_edit.html', RequestContext(request, {'form':form}))

def create(request):

    course = Course()
    cskey = request.session.get('course_season_key',None)
    if not cskey is None:
        season =  Season.get(str(cskey))
    cfkey = request.session.get('course_folder_key',None)
    if not cfkey is None:
        folder =  Folder.get(str(cfkey))

    if not( (folder is None) or (Season is None) ):
        course.folder_key = cfkey
        course.season_key = cskey



    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.mark_as_modify()
            course.save()
            return HttpResponseRedirect('..')
    else:
        form = CourseForm(instance=course)
    return render_to_response('admin/courses_create.html', RequestContext(request, {'form':form}))

def recount(request, course_id):

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})

    return HttpResponseRedirect("../..")


def delete(request, course_id):

    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    taskqueue.add(url='/task/hide_course_students/', params={'course_id':course.key().id()})

    course.hidden = True
    course.mark_as_modify()
    course.save()

    return redirect("../..")


    

