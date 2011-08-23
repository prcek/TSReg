# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Student,Course
import utils.config as cfg
import utils.mail as mail
import logging


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
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=YEAR_CHOICES))
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    post_code = forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False)
    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False)

    class Meta:
        model = Student
        fields = ( 'course_key', 'addressing', 'name', 'surname', 'email', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'comment' )

    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['course_key']._set_choices(Course.get_COURSE_CHOICES())

        

def index(request):
    student_list=Student.list()

    return render_to_response('admin/students_index.html', RequestContext(request, { 'student_list': student_list }))

def index_course(request, course_id):
    course = Course.get_by_id(int(course_id))  
    student_list=Student.list_for_course(course.key())

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
    student.init_reg()
    student.init_ref_base()
    student.reg_by_admin = True
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('create student before %s'% student)
            form.save(commit=False)
            logging.info('create student after %s'% student)
            student.save()
            student.init_ref_codes()
            student.save()
            return redirect('..')
    else:
        form = StudentForm(instance=student)
    return render_to_response('admin/students_create.html', RequestContext(request, {'form':form}))


def email(request,student_id):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404
    course = student.get_course()

    (check_subject,check_text) = mail.prepare_check_email_text(student,course)
    (confirm_subject,confirm_text) = mail.prepare_confirm_email_text(student,course)
    (enroll_yes_subject,enroll_yes_text) = mail.prepare_enroll_yes_email_text(student,course)
    (enroll_no_subject,enroll_no_text) = mail.prepare_enroll_no_email_text(student,course)

    return render_to_response('admin/students_email.html', RequestContext(request, {
        'check_subject':check_subject,
        'check_text':check_text,
        'confirm_subject':confirm_subject,
        'confirm_text':confirm_text,
        'enroll_yes_subject':enroll_yes_subject,
        'enroll_yes_text':enroll_yes_text,
        'enroll_no_subject':enroll_no_subject,
        'enroll_no_text':enroll_no_text,
    }))
