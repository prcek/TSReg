# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Student
import utils.config as cfg
import logging


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}


class StudentForm(forms.ModelForm):
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)

    class Meta:
        model = Student
        fields = ( 'name' )

def index(request):
    student_list=Student.list()

    return render_to_response('admin/students_index.html', RequestContext(request, { 'student_list': student_list }))



def edit(request, student_id):

    student = Student.get_by_id(int(student_id))

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('edit student before %s'% student)
            form.save(commit=False)
            logging.info('edit student after %s'% student)
            student.save()
            return redirect('../..')
    else:
        form = StudentForm(instance=student)

    return render_to_response('admin/students_edit.html', RequestContext(request, {'form':form}))

def create(request):

    student = Student()
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('create student before %s'% student)
            form.save(commit=False)
            logging.info('create student after %s'% student)
            student.save()
            return redirect('..')
    else:
        form = StudentForm(instance=student)
    return render_to_response('admin/students_create.html', RequestContext(request, {'form':form}))


