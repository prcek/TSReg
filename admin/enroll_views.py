# -*- coding: utf-8 -*-


from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Folder,Course,Student
from enroll.views import get_offer_list2
from utils import captcha
from utils import config

from admin.queue import plan_send_student_email, plan_update_course, plan_send_enroll_form

import logging
import os


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


def index(request):

    offer = get_offer_list2()
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None


    if 'enable' in request.GET:
        config.setConfigBool('ENROLL_ENROLL_ON',True)
    if 'disable' in request.GET:
        config.setConfigBool('ENROLL_ENROLL_ON',False)


    enroll_on =  config.getConfigBool('ENROLL_ENROLL_ON',False)

    return render_to_response('admin/enroll_index.html', RequestContext(request, { 'offer':offer , 'preview':True, 'enroll_on':enroll_on}))

class ConfirmForm(forms.Form):
    ref_code = forms.CharField(label='referenční kód', error_messages=ERROR_MESSAGES,required=False)
    confirm_code = forms.CharField(label='potvrzovací kód', error_messages=ERROR_MESSAGES,required=False)
    
def manual_confirm(request):
    info=''
    student=None
    course=None
    status=False
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data['ref_code']
            confirm_code = form.cleaned_data['confirm_code']
            student = Student.get_by_ref_key(ref_code)
            if student is None:
                student = Student.get_by_confirm_key(confirm_code)
            if student is None:
                info = "Přihláška nenalezena"
            else:
                course = Course.get(student.course_key) 
                if course is None:
                    info = "Přihláška obsahuje neplatný kurz"
                else:
                    if student.status == 'n':
                        if course.can_enroll():
                            student.status = 'e'
                            student.init_enroll()
                            student.save()
                            plan_send_student_email('ENROLL_OK_PAY_REQUEST',student)
                            info = "Přihláška byla potvrzena a zařazena do kurzu"
                        else:
                            student.status = 's'
                            student.save()
                            plan_send_student_email('ENROLL_OK_SPARE',student)
                            info = "Přihláška byla potvrzena a zařazena do kurzu mezi náhradníky"
               
                        plan_send_enroll_form(student) 
                        plan_update_course(course)
                        status=True
                    elif student.status in ['e','s']:
                        info = "Přihláška již byla potrzena"
                    else:
                        info = "Přihlášku již nelze potvrdit"
    else:
        form = ConfirmForm()
    return render_to_response('admin/enroll_manual_confirm.html', RequestContext(request, { 'form':form, 'student':student, 'course':course, 'status':status, 'info':info }))
    
