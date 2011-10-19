# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
#from google.appengine.api import taskqueue

from enroll.models import Student,Course
from admin.queue import plan_send_student_email, plan_update_course, plan_job_transfer_students, plan_job_card_for_students, plan_job_invitation_for_students
from admin.student_sort import sort_students_single, sort_students_school, sort_students_pair, sort_students_spare_single, sort_students_spare_school, sort_students_spare_pair
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

ADD_CHOICES = (
    ('e','zapsaného'),
    ('s','náhradníka')
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

    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES)
    no_email_info = forms.BooleanField(label='ne informace', error_messages=ERROR_MESSAGES, required=False)
    no_email_ad = forms.BooleanField(label='ne reklamu', error_messages=ERROR_MESSAGES, required=False)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    long_period = forms.BooleanField(label='celoroční', error_messages=ERROR_MESSAGES, required=False)
    to_pay = forms.IntegerField(label='cena', error_messages=ERROR_MESSAGES)
    balance_due = forms.IntegerField(label='doplatek', error_messages=ERROR_MESSAGES,  required=False)
    discount = forms.CharField(label='sleva', error_messages=ERROR_MESSAGES, required=False)
    paid_ok = forms.BooleanField(label='zaplaceno', error_messages=ERROR_MESSAGES, required=False)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=YEAR_CHOICES))
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    post_code = forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False)
    school = forms.CharField(label='škola', error_messages=ERROR_MESSAGES, required=False)
    school_class = forms.CharField(label='třída', error_messages=ERROR_MESSAGES, required=False)
    partner_ref_code = forms.CharField(label='kód partnera', error_messages=ERROR_MESSAGES, required=False)
    comment = forms.CharField(label='poznámka', error_messages=ERROR_MESSAGES, required=False)


    def clean_addressing(self):
        data = self.cleaned_data['addressing']
        if not data in ['p','s','d']:
            raise forms.ValidationError(ERROR_MESSAGES['required'])
        return data

    class Meta:
        model = Student
        fields = ( 'addressing', 'name', 'surname', 'email', 'no_email_info', 'no_email_ad', 'student','long_period', 'to_pay', 'balance_due', 'discount', 'paid_ok', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'school', 'school_class', 'partner_ref_code', 'comment' )

#    def __init__(self,data = None, **kwargs):
#        super(self.__class__,self).__init__(data, **kwargs)
#        self.fields['course_key']._set_choices(Course.get_COURSE_CHOICES())


class StudentFormAdd(StudentForm):
    add_mode = forms.CharField(label='přidat jako', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADD_CHOICES))
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
        fields = ( 'addressing', 'name', 'surname', 'email', 'no_email_info', 'no_email_ad', 'student','long_period', 'to_pay', 'paid_ok', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'partner_ref_code', 'comment' )

   

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

    if course.group_mode == 'Single':
        student_list_to_enroll = sort_students_spare_single(student_list_to_enroll)
        student_list_enrolled = sort_students_single(student_list_enrolled)
    elif course.group_mode == 'School':
        student_list_to_enroll = sort_students_spare_school(student_list_to_enroll)
        student_list_enrolled = sort_students_school(student_list_enrolled)
    elif course.group_mode == 'Pair':
        student_list_to_enroll = sort_students_spare_pair(student_list_to_enroll)
        student_list_enrolled = sort_students_pair(student_list_enrolled)

    

    return render_to_response('admin/course_students.html', RequestContext(request, { 
        'course': course,
        'student_list_to_enroll': student_list_to_enroll,  
        'student_list_enrolled': student_list_enrolled,  
    }))

def action_course(request,course_id):
    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404


    if request.method == 'POST':
        logging.info(request.POST)
        if 'operation' in request.POST:
            op = request.POST['operation']
        else:
            op = None

        if 'enroll_select' in request.POST:
            en_sel = request.POST.getlist('enroll_select')
        else:
            en_sel = [] 

        if 'spare_select' in request.POST:
            sp_sel = request.POST.getlist('spare_select')
        else:
            sp_sel = [] 

        if 'all_select' in request.POST:
            all_sel = request.POST.getlist('all_select')
        else:
            all_sel = []
            all_sel.extend(en_sel)
            all_sel.extend(sp_sel)

        logging.info('en_sel=%s, spare_sel=%s, all_sel=%s'%(en_sel,sp_sel,all_sel))

        if 'course_key' in request.POST:
            target_course = Course.get(request.POST['course_key'])
        else:
            target_course = None
        

        if op == 'action_transfer':
            return action_do_transfer(request, source_course=course, student_ids = all_sel, target_course=target_course)

        if op == 'action_card':
            return action_do_card(request, source_course=course, student_ids = all_sel)

        if op == 'action_invitation':
            return action_do_invitation(request, source_course=course, student_ids = all_sel)

        if op == 'action_pair':
            return action_do_pair(request, source_course=course, student_ids = all_sel)



    logging.info('unhandled action!')

    return HttpResponseRedirect('../')

class TransferPickForm(forms.Form):
    course_key = forms.ChoiceField(label='Do kurzu')
    def __init__(self, data = None, courses = []):
        super(self.__class__,self).__init__(data)
#        if not label is None:
#            self.fields['course_key'].label=label
        self.fields['course_key'].choices=courses



def action_do_transfer(request, source_course=None, student_ids=None, target_course=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_transfer.html', RequestContext(request, {'info':info}))

    if target_course is None:

        info = 'přeřazení žáků do jiného kurzu'
        form = TransferPickForm(courses = Course.get_COURSE_CHOICES())

        return render_to_response('admin/action_transfer.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))

    job_id=plan_job_transfer_students(request.auth_info.email,student_ids,source_course, target_course)


    return HttpResponseRedirect('../wait/%d/'%job_id)


class CardPickForm(forms.Form):
    course_code = forms.CharField(required=False, label='Kód kurzu')
    season_name = forms.CharField(required=False, label='Sezóna')
    info_line_1 = forms.CharField(required=False, label='1. řádek')
    info_line_2 = forms.CharField(required=False, label='2. řádek')
   
    def __init__(self, data = None, course = None):
        super(self.__class__,self).__init__(data)
        if not course is None:
            self.fields['course_code'].initial = course.code
            self.fields['season_name'].initial = course.season_name()
            self.fields['info_line_1'].initial = course.card_line_1
            self.fields['info_line_2'].initial = course.card_line_2

    
def action_do_card(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_card.html', RequestContext(request, {'info':info}))

    if not 'season_name' in request.POST:
        form = CardPickForm(course = source_course)
        info = 'generování průkazek' 
        return render_to_response('admin/action_card.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))
   
    form = CardPickForm(request.POST)
    if form.is_valid():
        course_code = form.cleaned_data['course_code']
        season_name = form.cleaned_data['season_name']
        info_line_1 = form.cleaned_data['info_line_1']
        info_line_2 = form.cleaned_data['info_line_2']
        job_id=plan_job_card_for_students(request.auth_info.email,student_ids,course_code, season_name, info_line_1, info_line_2)
        return HttpResponseRedirect('../wait/%d/'%job_id)


    info = 'generování průkazek' 
    return render_to_response('admin/action_card.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))
  
INVITATION_MODE_CHOICES = (
    ('direct','přímá adresa'),
    ('parents','adresa rodičům'),
)

        
class InvitationPickForm(forms.Form):
    addressing_parents = forms.CharField(required=False, label='Oslovení pro rodiče', initial='Vážení rodiče')
    addressing_p = forms.CharField(required=False, label='Oslovení pro pána', initial='Vážený pan')
    addressing_s = forms.CharField(required=False, label='Oslovení pro slečnu', initial='Vážená slečna')
    addressing_d = forms.CharField(required=False, label='Oslovení pro paní', initial='Vážená paní')
    mode  = forms.CharField(label='Typ adresy', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=INVITATION_MODE_CHOICES), initial='parents')
   
    def __init__(self, data = None, course = None):
        super(self.__class__,self).__init__(data)
        if not course is None:
#TODO preselect mode by course type
            pass

def action_do_invitation(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_invitation.html', RequestContext(request, {'info':info}))

    if not 'mode' in request.POST:
        form = InvitationPickForm(course = source_course)
        info = 'generování adres' 
        return render_to_response('admin/action_invitation.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))
   
    form = InvitationPickForm(request.POST)
    if form.is_valid():
        mode  = form.cleaned_data['mode']
        addressing_parents = form.cleaned_data['addressing_parents']
        addressing_p= form.cleaned_data['addressing_p']
        addressing_s= form.cleaned_data['addressing_s']
        addressing_d= form.cleaned_data['addressing_d']
        job_id=plan_job_invitation_for_students(request.auth_info.email,student_ids,mode,addressing_parents, addressing_p, addressing_s,addressing_d)
        return HttpResponseRedirect('../wait/%d/'%job_id)


    info = 'generování adres' 
    return render_to_response('admin/action_invitation.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))

def action_do_pair(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)

    if (student_ids is None) or (len(student_ids)!=2):
        info = 'musí být označeni právě dva žáci'
        return render_to_response('admin/action_pair.html', RequestContext(request, {'info':info}))
    
    s1 = Student.get_by_id(int(student_ids[0])) 
    s2 = Student.get_by_id(int(student_ids[1])) 

    if s1 is None or s2 is None:
        raise Http404

    s1.partner_ref_code = s2.ref_key
    s2.partner_ref_code = s1.ref_key

    s1.save()
    s2.save()


    for s in Student.list_by_partner(s1.ref_key):
        if s.key().id != s2.key().id:
            s.partner_ref_code=""
            s.save()
    
    for s in Student.list_by_partner(s2.ref_key):
        if s.key().id != s1.key().id:
            s.partner_ref_code=""
            s.save()
 
    return redirect('..')


def edit(request, student_id,course_id=None):

    student = Student.get_by_id(int(student_id))
    if student is None:
        logging.info('student is None') 
        raise Http404


    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('edit student before %s'% student)
            form.save(commit=False)
            logging.info('edit student after %s'% student)
            student.save()

            course_id = student.get_course_id()
            logging.info('student course_id = %s'%(course_id))
            plan_update_course(course_id)

            return redirect('../..')
    else:
        form = StudentForm(instance=student)

    return render_to_response('admin/students_edit.html', RequestContext(request, {'form':form}))

def create(request, course_id):

    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404

    student = Student()
    student.set_course_key(str(course.key()))
    student.init_reg()
    student.init_ref_base()
    student.reg_by_admin = True
    student.status = '-'
    if request.method == 'POST':
        form = StudentFormAdd(request.POST, instance=student)
        if form.is_valid():
            logging.info('create student before %s'% student)
            form.save(commit=False)
            student.status =  form.cleaned_data['add_mode']
            if student.status=='e':
                student.init_enroll()
            logging.info('create student after %s'% student)
            student.save()
            student.init_ref_codes()
            student.save()

            course_id = student.get_course_id()
            plan_update_course(course_id)

            return redirect('..')
    else:
        form = StudentFormAdd(instance=student)
    return render_to_response('admin/students_create.html', RequestContext(request, {'form':form}))


def email(request,student_id,course_id=None):
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
        student.init_enroll()
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

    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404
    course = student.get_course()



    return render_to_response('admin/students_view.html', RequestContext(request, {
        'student':student,'course':course
    }))

 

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

def enroll_as_pdf(request, course_id):

    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404

    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote("prihlasky_%s.pdf"%course.code)
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_enroll

    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    students = []
    students.extend(student_list_enrolled)
    students.extend(student_list_to_enroll)

    students_enroll(r,students)
    return r

