from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Course
import utils.config as cfg
import logging



class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ( 'active', 'order_value', 'code','name', 'category', 'group_mode', 'capacity', 'pending_limit' )

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


