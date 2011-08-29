# -*- coding: utf-8 -*-


from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Folder,Course,Student
from utils import captcha
from utils import config

from google.appengine.api import taskqueue

import logging
import os


ADDRESSING_CHOICES = (
    ('-',''),
    ('p','Pan'),
    ('s','Slečna'),
    ('d','Paní'),
)

YEAR_CHOICES = [
    (0,'')
]

ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


for x in range(1900,2011):
    YEAR_CHOICES.append((x,x))

class EnrollForm(forms.Form):
    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=YEAR_CHOICES))
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    post_code = forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False)
    partner = forms.CharField(label='ref. kód partnera', error_messages=ERROR_MESSAGES, required=False)


    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False)


def goto_index(request):
    return redirect('/zapis/')

def get_offer_list():
    folders_query=Folder.list()
    courses_query=Course.list_for_enroll()  

    folders= set([])
    courses = []
    result = []
    for course in courses_query:
        folders.add(course.folder_key)
        courses.append(course)

    logging.info(folders)
    logging.info(courses)

    for folder in folders_query:
        fk = str(folder.key())
        logging.info('fk:%s'%fk)
        if fk in folders:
            logging.info('in')
            sub_list = [c for c in courses if fk==c.folder_key] 
            result.append({'folder':folder, 'courses':sub_list })
            pass

    return result

def index(request):
    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        return render_to_response('enroll/index_off.html', RequestContext(request))

#    folder_list=Folder.list().fetch(200)
#
#    if len(folder_list) == 0:
#        folder_list = None
#
#    course_list=Course.list_for_enroll().fetch(200)
#    if len(course_list) == 0:
#        course_list=None

    offer = get_offer_list()
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None

    return render_to_response('enroll/index.html', RequestContext(request, { 'offer':offer }))

def attend(request,course_id):


    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        raise Http404

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404
    if not course.is_open():
        raise Http404

    captcha_error = None

    if request.method == 'POST':
        form = EnrollForm(request.POST)

        if form.is_valid():
            check_ok = False
            if config.getConfigBool('CAPTCHA_ON',False):
                if captcha.check(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], os.environ['REMOTE_ADDR'],  config.getConfigString('CAPTCHA_PRIVATE_KEY','')):
                    check_ok = True
                else:
                    captcha_error = True
                    logging.info('captcha wrong')
            else:
                check_ok = True

            if check_ok:
                logging.info('creating new student record')    
                st = Student()
                st.status = 'n'
                st.course_key=str(course.key())
                st.init_reg()
                st.init_ref_base()
                st.addressing = form.cleaned_data['addressing']
                st.name = form.cleaned_data['name']
                st.surname = form.cleaned_data['surname']
                st.student = form.cleaned_data['student']
                st.year = form.cleaned_data['year']
                st.email = form.cleaned_data['email']
                st.phone = form.cleaned_data['phone']
                st.street = form.cleaned_data['street']
                st.street_no = form.cleaned_data['street_no']
                st.city = form.cleaned_data['city']
                st.post_code = form.cleaned_data['post_code']
                st.comment = form.cleaned_data['comment']
                st.partner_ref_code = form.cleaned_data['partner']


                if (st.student):
                    st.to_pay = course.cost_student
                else:
                    st.to_pay = course.cost_full

                st.save()
                st.init_ref_codes()
                st.save()
                ref_code = st.ref_key
                taskqueue.add(url='/task/send_check_email/', params={'student_id':st.key().id()})         
                return HttpResponseRedirect('/zapis/prihlaska/%s/'%ref_code)

    else:
        form = EnrollForm()
    
    if (config.getConfigBool('CAPTCHA_ON',False)):
        html_captcha = captcha.displayhtml(config.getConfigString('CAPTCHA_PUBLIC_KEY',''))
    else:
        html_captcha = None

    return render_to_response('enroll/attend.html', RequestContext(request, { 'course': course, 'form':form , 'html_captcha': html_captcha, 'captcha_error':captcha_error}))




def show(request,ref_code):
    student = Student.get_by_ref_key(ref_code)
    if student:
        course = Course.get(student.course_key) 
    else:
        course = None
    return render_to_response('enroll/show.html', RequestContext(request, { 'course': course, 'student':student, 'ref_code':ref_code }))

def confirm(request,confirm_code):
    student = Student.get_by_confirm_key(confirm_code)
    if student:
        course = Course.get(student.course_key) 
    else:
        course = None

    if (student is None) or (course is None):
        status = False
    else:
        status = True

    if status:
        if student.status == 'n':
            student.status = 'nc'
            student.save()
            taskqueue.add(url='/task/send_confirm_email/', params={'student_id':student.key().id()})         
            taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})
        elif student.status != 'nc':
            status = False

    return render_to_response('enroll/confirm.html', RequestContext(request, { 'course': course, 'student':student, 'confirm_code':confirm_code, 'status':status }))
    
        
