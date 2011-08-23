# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from google.appengine.api import taskqueue


from enroll.models import Course
import utils.config as cfg
import logging


GROUP_MODE_CHOICES = (
    ('Single','jednotlivci'),
    ('Pair','po párech'),
)
ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}


class CourseForm(forms.ModelForm):
    active = forms.BooleanField(label='aktivní', required=False, help_text='je-li kurz aktivní, bude nabízen pro zápis')
    order_value = forms.IntegerField(label='řazení',error_messages=ERROR_MESSAGES, help_text='kurzy budou tříděny podle tohodle čísla v zestupném pořadí')
    code = forms.CharField(label='kód', error_messages=ERROR_MESSAGES)
    name = forms.CharField(label='název', error_messages=ERROR_MESSAGES)
    category = forms.CharField(label='kategorie', error_messages=ERROR_MESSAGES)
    period = forms.CharField(label='termín', error_messages=ERROR_MESSAGES)
    first_period = forms.CharField(label='první lekce', error_messages=ERROR_MESSAGES)
    group_mode = forms.CharField(label='režim', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=GROUP_MODE_CHOICES)) 
    capacity = forms.IntegerField(label='kapacita', error_messages=ERROR_MESSAGES)
    pending_limit = forms.IntegerField(label='fronta', error_messages=ERROR_MESSAGES)


    class Meta:
        model = Course
        fields = ( 'active', 'order_value', 'code','name', 'category', 'period', 'first_period', 'group_mode', 'capacity', 'pending_limit' )

    def clean_code(self):
        data = self.cleaned_data['code']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data

def index(request):
    course_list=Course.list()

    return render_to_response('admin/courses_index.html', RequestContext(request, { 'course_list': course_list }))



def edit(request, course_id):

    course = Course.get_by_id(int(course_id))

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.save()
            return redirect('../..')
    else:
        form = CourseForm(instance=course)

    return render_to_response('admin/courses_edit.html', RequestContext(request, {'form':form}))

def create(request):

    course = Course()
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.save()
            return redirect('..')
    else:
        form = CourseForm(instance=course)
    return render_to_response('admin/courses_create.html', RequestContext(request, {'form':form}))

def recount(request, course_id):

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})

    return redirect("../..")

