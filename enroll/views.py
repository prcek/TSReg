# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Folder,Course,Student
from utils import captcha
from utils import config

from admin.queue import plan_send_student_email, plan_update_course, plan_send_enroll_form


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


for x in reversed(range(1900,2016)):
    YEAR_CHOICES.append((x,x))

class EnrollForm(forms.Form):
    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES, max_length=30)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES, max_length=30)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES, max_length=100)
    no_email_ad = forms.BooleanField(label='nezasílat reklamu', error_messages=ERROR_MESSAGES, required=False)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False, max_length=30)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    long_period = forms.BooleanField(label='celoroční', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=YEAR_CHOICES))
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False, max_length=50)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False, max_length=20)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False, max_length=30)
    post_code = forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False, max_length=10)
    school = forms.CharField(label='škola', error_messages=ERROR_MESSAGES, required=False, max_length=50)
    school_class = forms.CharField(label='třída', error_messages=ERROR_MESSAGES, required=False, max_length=15)
#    partner = forms.CharField(label='ref. kód partnera', error_messages=ERROR_MESSAGES, required=False)
#    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False, widget=forms.Textarea(attrs={'cols':30, 'rows':3}))
    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False, max_length=100)

    def clean_addressing(self):
        data = self.cleaned_data['addressing']
        if not data in ['p','s','d']:
            raise forms.ValidationError(ERROR_MESSAGES['required'])
        return data

def goto_index(request):
    return HttpResponseRedirect('/zapis/')

def get_offer_list(folder_id = None):

    if folder_id is None:
        folders_query=Folder.list()
    else:
        folders_query = []
        f = Folder.get_by_id(int(folder_id))
        if f:
            folders_query.append(f)
    
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

def get_offer_list2():
    courses_query=Course.list_for_enroll()  
    folder_courses= dict()
    result = []
    for course in courses_query:
        folder_courses.setdefault(course.folder_key,[]).append(course)         

    result=[]
    folders_query=Folder.list()
    for folder in folders_query:
        if str(folder.key()) in folder_courses:
            result.append({'folder':folder, 'courses':folder_courses[str(folder.key())]})
            
    logging.info(result)
   
    return result


def index(request):


    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        return render_to_response('enroll/index_off.html', RequestContext(request))

    offer = get_offer_list()
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None

    return render_to_response('enroll/index.html', RequestContext(request, { 'offer':offer }))

def folder_index(request,folder_id):
    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        return render_to_response('enroll/index_off.html', RequestContext(request))

    offer = get_offer_list(folder_id)
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None

    return render_to_response('enroll/folder_index.html', RequestContext(request, { 'offer':offer }))

def form2student(form,course):
    st = Student()
    st.status = 'n'
    st.course_key=str(course.key())
    st.init_reg()
    st.init_ref_base()
    st.addressing = form.cleaned_data['addressing']
    st.name = form.cleaned_data['name']
    st.surname = form.cleaned_data['surname']
    st.student = form.cleaned_data['student']
    st.long_period = form.cleaned_data['long_period']
    st.year = form.cleaned_data['year']
    st.email = form.cleaned_data['email']
    st.no_email_ad = form.cleaned_data['no_email_ad']
    st.phone = form.cleaned_data['phone']
    st.street = form.cleaned_data['street']
    st.street_no = form.cleaned_data['street_no']
    st.city = form.cleaned_data['city']
    st.post_code = form.cleaned_data['post_code']
    st.school = form.cleaned_data['school']
    st.school_class = form.cleaned_data['school_class']
    st.comment = form.cleaned_data['comment']
    #st.partner_ref_code = form.cleaned_data['partner']

    if course.cost_sale:
        a = course.cost_sa
        b = course.cost_sb
    else:
        a = course.cost_a
        b = course.cost_b
    
    if course.cost_mode == 'Normal':
        if (st.student):
            st.course_cost = b
        else:
            st.course_cost = a
    elif course.cost_mode == 'Period':
        if (st.long_period):
            st.course_cost = a 
        else:
            st.course_cost = b
    elif course.cost_mode == 'Fix':
        st.course_cost = a


    st.save()
    st.init_ref_codes()
    st.save()
    return st


def attend_single(request,course):
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
                st = form2student(form,course)
                ref_code = st.ref_key
                plan_send_student_email('ENROLL_CHECK',st)
                plan_update_course(course)
                return HttpResponseRedirect('/zapis/prihlaska/%s/'%ref_code)

    else:
        form = EnrollForm()
    
    if (config.getConfigBool('CAPTCHA_ON',False)):
        html_captcha = captcha.displayhtml(config.getConfigString('CAPTCHA_PUBLIC_KEY',''))
    else:
        html_captcha = None

    return render_to_response('enroll/attend.html', RequestContext(request, { 'course': course, 'form':form , 'html_captcha': html_captcha, 'captcha_error':captcha_error}))


   
def attend_pair(request,course):
    captcha_error = None

    if request.method == 'POST':
        form1 = EnrollForm(request.POST,prefix='p1')
        form2 = EnrollForm(request.POST,prefix='p2')

        if form1.is_valid() and form2.is_valid():
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
                st1 = form2student(form1,course)
                st2 = form2student(form2,course)

                st1.partner_ref_code = st2.ref_key
                st2.partner_ref_code = st1.ref_key
                st1.save()
                st2.save()

                ref_code1 = st1.ref_key
                ref_code2 = st2.ref_key
                plan_send_student_email('ENROLL_CHECK',st1)
                plan_send_student_email('ENROLL_CHECK',st2)
                plan_update_course(course)
                return HttpResponseRedirect('/zapis/prihlasky/%s/%s/'%(ref_code1,ref_code2))

    else:
        form1 = EnrollForm(prefix='p1')
        form2 = EnrollForm(prefix='p2')
    
    if (config.getConfigBool('CAPTCHA_ON',False)):
        html_captcha = captcha.displayhtml(config.getConfigString('CAPTCHA_PUBLIC_KEY',''))
    else:
        html_captcha = None

    return render_to_response('enroll/attend_pair.html', RequestContext(request, { 'course': course, 'form1':form1, 'form2':form2 , 'html_captcha': html_captcha, 'captcha_error':captcha_error}))



def attend(request,course_id):


    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        raise Http404

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404
    if not course.is_open():
        raise Http404

    if course.only_pair_enroll():
        return attend_pair(request,course)
    else:
        return attend_single(request,course)


def attend_force_single(request,course_id):


    if not config.getConfigBool('ENROLL_ENROLL_ON',False):
        raise Http404

    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404
    if not course.is_open():
        raise Http404

    return attend_single(request,course)


def show(request,ref_code):
    student = Student.get_by_ref_key(ref_code)
    if student:
        course = Course.get(student.course_key) 
    else:
        course = None
    return render_to_response('enroll/show.html', RequestContext(request, { 'course': course, 'student':student, 'ref_code':ref_code }))

def show_pair(request,ref_code1, ref_code2):
    student1 = Student.get_by_ref_key(ref_code1)
    if student1:
        course = Course.get(student1.course_key) 
    else:
        course = None
    student2 = Student.get_by_ref_key(ref_code2)
 
    
    return render_to_response('enroll/show_pair.html', RequestContext(request, { 'course': course, 'student1':student1, 'ref_code1':ref_code1, 'student2':student2, 'ref_code2':ref_code2 }))


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
            if course.can_enroll():
                student.status = 'e'
                student.init_enroll()
                student.save()
                plan_send_student_email('ENROLL_OK_PAY_REQUEST',student)
            else:
                student.status = 's'
                student.save()
                plan_send_student_email('ENROLL_OK_SPARE',student)
               
            plan_send_enroll_form(student) 
            plan_update_course(course)

        elif not student.status in ['e','s']:
            status = False

    return render_to_response('enroll/confirm.html', RequestContext(request, { 'course': course, 'student':student, 'confirm_code':confirm_code, 'status':status }))
    

def confirm_pair(request,confirm_code1,confirm_code2):
    student1 = Student.get_by_confirm_key(confirm_code1)
    if student1:
        course = Course.get(student1.course_key) 
    else:
        course = None

    student2 = Student.get_by_confirm_key(confirm_code2)

    if (student1 is None) or (student2 is None) or (course is None):
        status = False
    else:
        status = True

    if status:
        if student1.status == 'n':
            if course.can_enroll():
                student1.status = 'e'
                student1.init_enroll()
                student1.save()
                plan_send_student_email('ENROLL_OK_PAY_REQUEST',student1)
            else:
                student1.status = 's'
                student1.save()
                plan_send_student_email('ENROLL_OK_SPARE',student1)
               
            plan_send_enroll_form(student1) 
            status1 = True
        
        elif not student1.status in ['e','s']:
            status1 = False
        else:
            status1 = True
            
        if student2.status == 'n':
            if course.can_enroll():
                student2.status = 'e'
                student2.init_enroll()
                student2.save()
                plan_send_student_email('ENROLL_OK_PAY_REQUEST',student2)
            else:
                student2.status = 's'
                student2.save()
                plan_send_student_email('ENROLL_OK_SPARE',student2)
               
            plan_send_enroll_form(student2) 

            status2 = True
        elif not student2.status in ['e','s']:
            status2 = False
        else:
            status2 = True
 

            
        status = status1 or status2            
        if status:
            plan_update_course(course)

    return render_to_response('enroll/confirm_pair.html', RequestContext(request, { 'course': course, 'student1':student1, 'student2':student2, 'confirm_code1':confirm_code1, 'confirm_code2':confirm_code2 , 'status':status }))
   
def smernice(request):
    return render_to_response('enroll/smernice.html', RequestContext(request, {  }))
     
