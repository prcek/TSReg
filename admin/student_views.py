# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
#from google.appengine.api import taskqueue

from enroll.models import Student,Course
from admin.queue import plan_send_student_email, plan_update_course
import utils.config as cfg
import utils.mail as mail
import utils.pdf as pdf
import logging
import urllib



ADDRESSING_CHOICES = (
    ('-',''),
    ('p','Pan'),
    ('s','Slečna'),
    ('d','Paní'),
)

YEAR_CHOICES = [
    (0,'')
]

for x in range(1900,2011):
    YEAR_CHOICES.append((x,x))

ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}

class CourseField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Course.get_COURSE_CHOICES())
        return super(CourseField,self).valid_value(value)



class StudentForm(forms.ModelForm):
#    course_key = forms.ChoiceField(label='kurz', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=Course.get_COURSE_CHOICES()))
#    course_key = forms.ChoiceField(label='kurz', error_messages=ERROR_MESSAGES, choices=Course.get_COURSE_CHOICES())
#    course_key = forms.ChoiceField(label='kurz', error_messages=ERROR_MESSAGES)
    course_key = CourseField(label='kurz', error_messages=ERROR_MESSAGES)
    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES)
    no_email_info = forms.BooleanField(label='ne informace', error_messages=ERROR_MESSAGES, required=False)
    no_email_ad = forms.BooleanField(label='ne reklamu', error_messages=ERROR_MESSAGES, required=False)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    long_period = forms.BooleanField(label='celoroční', error_messages=ERROR_MESSAGES, required=False)
    to_pay = forms.IntegerField(label='cena', error_messages=ERROR_MESSAGES)
    paid_ok = forms.BooleanField(label='zaplaceno', error_messages=ERROR_MESSAGES, required=False)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=YEAR_CHOICES))
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    post_code = forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False)
    partner_ref_code = forms.CharField(label='kód partnera', error_messages=ERROR_MESSAGES, required=False)
    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False)


    def clean_addressing(self):
        data = self.cleaned_data['addressing']
        if not data in ['p','s','d']:
            raise forms.ValidationError(ERROR_MESSAGES['required'])
        return data

    class Meta:
        model = Student
        fields = ( 'course_key', 'addressing', 'name', 'surname', 'email', 'no_email_info', 'no_email_ad', 'student','long_period', 'to_pay', 'paid_ok', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'partner_ref_code', 'comment' )

    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['course_key']._set_choices(Course.get_COURSE_CHOICES())

class FindForm(forms.Form):
    ref_code = forms.CharField(label='referenční číslo', error_messages=ERROR_MESSAGES,required=False)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES,required=False)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES,required=False)
        

def index(request):

    if request.method == 'POST':
        student_list = [] 
        form = FindForm(request.POST)
        if form.is_valid():
            ref_code=form.cleaned_data['ref_code'].upper()
            surname = form.cleaned_data['surname']
            email = form.cleaned_data['email']
            logging.info("find: '%s' '%s' '%s'"%(ref_code,surname,email)) 
            if ref_code != '':
                rs = Student.get_by_ref_key(ref_code)
                if rs: 
                    student_list.append(rs)
            
            if surname != '':
                student_list.extend(Student.list_by_surname(surname).fetch(100))
                
            if email != '':
                student_list.extend(Student.list_by_email(email).fetch(100))
                  
            
    else:
        student_list = None
        form = FindForm()

  
    if student_list != None and len(student_list) == 0:
        not_found = True
    else:
        not_found = False


    return render_to_response('admin/students_index.html', RequestContext(request, { 'student_list': student_list, 'form':form , 'not_found':not_found}))

def index_course(request, course_id):
    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404
    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())


    return render_to_response('admin/course_students.html', RequestContext(request, { 
        'course': course,
        'student_list_to_enroll': student_list_to_enroll,  
        'student_list_enrolled': student_list_enrolled,  
    }))



def edit(request, student_id,course_id=None):

    student = Student.get_by_id(int(student_id))

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('edit student before %s'% student)
            form.save(commit=False)
            logging.info('edit student after %s'% student)
            student.save()

            course_id = student.get_course_id()
            plan_update_course(course_id)

            return redirect('../..')
    else:
        form = StudentForm(instance=student)

    return render_to_response('admin/students_edit.html', RequestContext(request, {'form':form}))

def create(request, course_id=None):

    student = Student()
    student.init_reg()
    student.init_ref_base()
    student.reg_by_admin = True
    student.status = 'nc'
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('create student before %s'% student)
            form.save(commit=False)
            logging.info('create student after %s'% student)
            student.save()
            student.init_ref_codes()
            student.save()

            course_id = student.get_course_id()
            plan_update_course(course_id)

            return redirect('..')
    else:
        form = StudentForm(instance=student)
    return render_to_response('admin/students_create.html', RequestContext(request, {'form':form}))


def email(request,student_id):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404
    course = student.get_course()


    emails = []
    for k in mail.MAIL_TEMPLATES:
        (subject,body) = mail.prepare_email_text(k, student,course)
        emails.append({'key':k, 'subject':subject, 'body':body}) 

    return render_to_response('admin/students_email.html', RequestContext(request, {
        'emails':emails
    }))

def enroll(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if student.status == 's':
        student.status = 'e'
        student.save()
        plan_send_student_email('CONFIRM_ENROLL_EMAIL', student)
        plan_update_course(course_id)

    return HttpResponseRedirect('../..')
    
def kick(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if (student.status == 's') or (student.status == 'e'):
        student.status = 'k'
        student.save()
        plan_send_student_email('NOTIFY_KICK_EMAIL', student)
        plan_update_course(course_id)
 
    return HttpResponseRedirect('../..')
 
def spare(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if (student.status == 'e') or (student.status == 'k'):
        student.status = 's'
        student.save()
        plan_update_course(course_id)
 
    return HttpResponseRedirect('../..')

def view(request,student_id,course_id=None):
    return HttpResponse('ok')
 

def course_emails(request, course_id):
    course = Course.get_by_id(int(course_id))  
    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    return render_to_response('admin/course_emails.html', RequestContext(request, { 
        'student_list_to_enroll': student_list_to_enroll,  
        'student_list_enrolled': student_list_enrolled,  
    }))

def course_as_csv(request, course_id):
    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404


    r =  HttpResponse(mimetype='application/vnd.ms-excel')
    file_name = urllib.quote("kurz_%s.csv"%course.code)
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.data import dump_to_csv

    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    students = []
    students.extend(student_list_enrolled)
    students.extend(student_list_to_enroll)

    data = [ ['#export kurz',course.code]]
    for s in students:
        data.append([s.ref_key,s.surname,s.name])
    dump_to_csv(data,r)
    return r

def course_as_pdf(request, course_id):

    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404

    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote("kurz_%s.pdf"%course.code)
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_table

    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    students = []
    students.extend(student_list_enrolled)
    students.extend(student_list_to_enroll)

    students_table(r,course,students)
    return r

