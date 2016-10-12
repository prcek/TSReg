# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
#from google.appengine.api import taskqueue

from enroll.models import Student,Course,Season
from admin.queue import plan_send_student_email, plan_update_course, plan_job_transfer_students, plan_job_card_for_students, plan_job_qcard_for_students, plan_job_invitation_for_students, plan_job_makecopy_students, plan_job_cardout_for_students, plan_job_hide_students
from admin.student_sort import sort_students_single, sort_students_school, sort_students_pair, sort_students_spare_single, sort_students_spare_school, sort_students_spare_pair, sort_students_kicked
import utils.config as cfg
import utils.mail as mail
import utils.pdf as pdf
from utils.qrcode import calc_qrcode_for_cmdcard
import utils.qrg
from utils.mail import valid_email,chunks
from utils.decorators import ar_edit
import logging
from operator import attrgetter
import urllib
import re
import utils.cdbsync as cdbsync
import base64


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


def is_valid_int(s):
    if s is None:
        return False
    try:
        r = int(s)
    except:
        return False
    return True

def is_pay_info(s):
    if s is None:
        return False

    if re.match('[^\d]+/[\d]+',s):
        return True
    return False
    


class CourseField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Course.get_COURSE_CHOICES())
        return super(CourseField,self).valid_value(value)



class StudentForm(forms.ModelForm):

    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES, required=False)
    no_email_notification = forms.BooleanField(label='nezasílat změny přihlášky', error_messages=ERROR_MESSAGES, required=False)
    no_email_info = forms.BooleanField(label='nezasílat informace', error_messages=ERROR_MESSAGES, required=False)
    no_email_ad = forms.BooleanField(label='nezasílat reklamu', error_messages=ERROR_MESSAGES, required=False)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    student_check = forms.BooleanField(label='st. ověřen', error_messages=ERROR_MESSAGES, required=False)
    long_period = forms.BooleanField(label='celoroční', error_messages=ERROR_MESSAGES, required=False)
    course_cost = forms.IntegerField(label='kurzovné', error_messages=ERROR_MESSAGES)
    paid = forms.IntegerField(label='platba', error_messages=ERROR_MESSAGES)
    discount = forms.CharField(label='sleva', error_messages=ERROR_MESSAGES, required=False)
    pay_info = forms.CharField(label='platební info', error_messages=ERROR_MESSAGES, required=False)
    card_out = forms.BooleanField(label='karta vydána', error_messages=ERROR_MESSAGES, required=False)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok nar.', error_messages=ERROR_MESSAGES, required=False)
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
        fields = ( 'addressing', 'name', 'surname', 'email', 'no_email_info', 'no_email_ad', 'no_email_notification', 'student', 'student_check', 'long_period', 'course_cost', 'paid', 'discount',  'pay_info', 'card_out', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'school', 'school_class', 'partner_ref_code', 'comment' )

#    def __init__(self,data = None, **kwargs):
#        super(self.__class__,self).__init__(data, **kwargs)
#        self.fields['course_key']._set_choices(Course.get_COURSE_CHOICES())


class StudentFormAdd(StudentForm):
    add_mode = forms.CharField(label='přidat jako', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADD_CHOICES))
    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ADDRESSING_CHOICES))
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES, required=False)
    no_email_notification = forms.BooleanField(label='nezasílat změny přihlášky', error_messages=ERROR_MESSAGES, required=False)
    no_email_info = forms.BooleanField(label='nezasílat informace', error_messages=ERROR_MESSAGES, required=False)
    no_email_ad = forms.BooleanField(label='nezasílat reklamu', error_messages=ERROR_MESSAGES, required=False)
    student = forms.BooleanField(label='student', error_messages=ERROR_MESSAGES, required=False)
    student_check = forms.BooleanField(label='st. ověřen', error_messages=ERROR_MESSAGES, required=False)
    long_period = forms.BooleanField(label='celoroční', error_messages=ERROR_MESSAGES, required=False)
    course_cost = forms.IntegerField(label='kurzovné', error_messages=ERROR_MESSAGES)
    paid = forms.IntegerField(label='platba', error_messages=ERROR_MESSAGES)
    discount = forms.CharField(label='sleva', error_messages=ERROR_MESSAGES, required=False)
    pay_info = forms.CharField(label='platební info', error_messages=ERROR_MESSAGES, required=False)
    card_out = forms.BooleanField(label='karta vydána', error_messages=ERROR_MESSAGES, required=False)
    phone = forms.CharField(label='telefon', error_messages=ERROR_MESSAGES, required=False)
    year = forms.IntegerField(label='rok nar.', error_messages=ERROR_MESSAGES, required=False)
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    school = forms.CharField(label='škola', error_messages=ERROR_MESSAGES, required=False)
    school_class = forms.CharField(label='třída', error_messages=ERROR_MESSAGES, required=False)
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
        fields = ( 'addressing', 'name', 'surname', 'email', 'no_email_info', 'no_email_ad', 'no_email_notification', 'student', 'student_check', 'long_period', 'course_cost', 'paid', 'discount',  'pay_info', 'card_out', 'phone', 'year', 'street', 'street_no', 'city', 'post_code', 'school', 'school_class', 'partner_ref_code', 'comment' )

class SeasonField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(Season.get_SEASON_CHOICES())
        return super(SeasonField,self).valid_value(value)
   

class FindForm(forms.Form):
#    season_key = SeasonField(label='v sezóně', error_messages=ERROR_MESSAGES)
    ref_code = forms.CharField(label='referenční číslo', error_messages=ERROR_MESSAGES,required=False)
    surname = forms.CharField(label='příjmení', error_messages=ERROR_MESSAGES,required=False)
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES,required=False)
        
#    def __init__(self,data = None, **kwargs):
#        super(self.__class__,self).__init__(data, **kwargs)
#        self.fields['season_key']._set_choices(Season.get_SEASON_CHOICES())


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

def index_course_kicked(request, course_id):
    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404




    student_list=Student.list_for_course_kicked(course.key())

    student_list = sort_students_kicked(student_list)
    

    return render_to_response('admin/course_students_kicked.html', RequestContext(request, { 
        'course': course,
        'student_list': student_list,  
    }))


class SeasonFilterForm(forms.Form):
    season_key = SeasonField(label='sezóna', error_messages=ERROR_MESSAGES)
    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['season_key']._set_choices(Season.get_SEASON_CHOICES())
 

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

        if 'season_key' in request.POST:
            target_season = Season.get(request.POST['season_key'])
        else:
            target_season = None


        if 'course_key' in request.POST:
            target_course = Course.get(request.POST['course_key'])
        else:
            target_course = None
        

        all_sel = filter(is_valid_int,all_sel)

        if op == 'action_transfer':
            return action_do_transfer(request, source_course=course, student_ids = all_sel, target_course=target_course, target_season=target_season)

        if op == 'action_makecopy':
            return action_do_makecopy(request, source_course=course, student_ids = all_sel, target_course=target_course, target_season=target_season)

        if op == 'action_card':
            return action_do_card(request, source_course=course, student_ids = all_sel)

        if op == 'action_qcard':
            return action_do_qcard(request, source_course=course, student_ids = all_sel)

        if op == 'action_invitation':
            return action_do_invitation(request, source_course=course, student_ids = all_sel)

        if op == 'action_pair':
            return action_do_pair(request, source_course=course, student_ids = all_sel)

        if op == 'action_cardout':
            return action_do_cardout(request, source_course=course, student_ids = all_sel)

        if op == 'action_delete':
            return action_do_delete(request, source_course=course, student_ids = all_sel)

        if op == 'action_email':
            return action_do_email(request, source_course=course, student_ids = all_sel)

        if op == 'action_enrollform':
            return action_do_enrollform(request, source_course=course, student_ids = all_sel)

        if op == 'action_extra':
            return action_do_extra(request, source_course=course, student_ids = all_sel)



    logging.info('unhandled action!')

    return HttpResponseRedirect('../')



SUBA_CHOICES=(
    ('email_check','kontrola emailu'),
    ('email_block_notif','nastavit notifikaci emailem'),
    ('email_block_info','nastavit info emaily'),
    ('email_block_ad','nastavit reklamni emaily'),
    ('addressing_d','osloveni na pani'),
    ('addressing_s','osloveni na slecna'),
    ('addressing_p','osloveni na pan'),
    ('student','nastavit studenta'),
    ('set_cost','nastavit kurzovne'),
    ('school2payinfo','skola do pl. infa'),
    ('discount2payinfo','sleva do pl. infa'),
)

class ExtraActionForm(forms.Form):
    sub_action = forms.CharField(label='akce', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=SUBA_CHOICES))
    bool_value = forms.BooleanField(label='ano/ne parametr', error_messages=ERROR_MESSAGES,  required=False)
    int_value = forms.IntegerField(label='ciselny parametr', error_messages=ERROR_MESSAGES,  required=False)
    str_value = forms.CharField(label='textovy parametr', error_messages=ERROR_MESSAGES,  required=False)
 

class TargetCoursePickForm(forms.Form):
    course_key = forms.ChoiceField(label='Do kurzu')
    def __init__(self, data = None, courses = []):
        super(self.__class__,self).__init__(data)
        self.fields['course_key'].choices=courses

       

@ar_edit
def action_do_extra(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)

    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_extra.html', RequestContext(request, {'info':info}))


    info = 'extra operace'
    if request.method=='POST' and 'sub_action' in request.POST:
        form = ExtraActionForm(request.POST)     
        if form.is_valid():
            suba = form.cleaned_data['sub_action']
            iv = form.cleaned_data['int_value']
            sv = form.cleaned_data['str_value']
            bv = form.cleaned_data['bool_value']
            for s_id in student_ids:
                s = Student.get_by_id(int(s_id))
                logging.info('s before: %s'%s)
                if not (s is None):
                    if suba=='email_check':
                        if not valid_email(s.email):
                            s.no_email_info = True
                            s.no_email_notification = True
                            s.no_email_ad = True
                            s.save()
                    elif suba=='email_block_notif':
                        s.no_email_notification = bv
                        s.save()
                    elif suba=='email_block_info':
                        s.no_email_info= bv
                        s.save()
                    elif suba=='email_block_ad':
                        s.no_email_ad= bv
                        s.save()
                    elif suba=='addressing_d':
                        s.addressing = 'd'
                        s.save()
                    elif suba=='addressing_s':
                        s.addressing = 's'
                        s.save()
                    elif suba=='addressing_p':
                        s.addressing = 'p'
                        s.save()
                    elif suba=='student':
                        s.student = bv
                        s.save()
                    elif suba=='set_cost':
                        logging.info('set_cost %s'%(iv))
                        s.course_cost = iv
                        s.save()
                    elif suba=='school2payinfo':
                        if (not (s.school is None)) and ((s.pay_info is None) or (s.pay_info=='')):
                            if is_pay_info(s.school):
                                s.pay_info = s.school
                                s.school = ""
                                s.save()                            
                    elif suba=='discount2payinfo':
                        if (not (s.discount is None)) and ((s.pay_info is None) or (s.pay_info=='')):
                            if is_pay_info(s.discount):
                                s.pay_info = s.discount
                                s.discount = ""
                                s.save() 

                    cdbsync.plan_cdb_put(s)

 
                logging.info('s after: %s'%s)

            
            return redirect('..')
    else:
        form = ExtraActionForm()     
 
    return render_to_response('admin/action_extra.html', RequestContext(request, { 'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))

class EmailFilterForm(forms.Form):
    email_ad = forms.BooleanField(label='včetně těch co nechtějí reklamy', error_messages=ERROR_MESSAGES, required=False, initial=True)
    email_info = forms.BooleanField(label='včetně těch co nechtějí žádné zpravy', error_messages=ERROR_MESSAGES, required=False)
    gsize = forms.IntegerField(label='skupinky po', error_messages=ERROR_MESSAGES,  required=True, initial=40)
 

def action_do_email(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)

    if source_course is None:
        raise Http404

    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_email.html', RequestContext(request, {'info':info}))

    if not 'gsize' in request.POST:
        form = EmailFilterForm()
        info = 'přehled vybraných emailů - zvol nastavení' 
        return render_to_response('admin/action_email.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))
   
    emails = None
    groups = None
    ecount = None
 
    form = EmailFilterForm(request.POST)
    if form.is_valid():
        info = 'přehled vybraných emailů' 

        studs = []
        studs.extend(Student.list_for_course_to_enroll(source_course.key()))
        studs.extend(Student.list_for_course_enrolled(source_course.key()))

        studs = filter(lambda x: str(x.key().id()) in student_ids,studs)
        

        if not form.cleaned_data['email_ad']:
            studs = filter(lambda x: not x.no_email_ad,studs)
        if not form.cleaned_data['email_info']:
            studs = filter(lambda x: not x.no_email_info,studs)

        if form.cleaned_data['gsize']:
            gsize = form.cleaned_data['gsize']
        else: 
            gsize = 0


        emails = map(attrgetter('email'),studs)
        emails = filter(valid_email,emails)
        emails = sorted(list(set(emails)))
        ecount = len(emails)            
          
        if (gsize) and (gsize>0): 
            groups = chunks(emails,gsize) 
        else:
            groups = [emails]

    else:
        info = 'přehled vybraných emailů - zvol nastavení' 

    return render_to_response('admin/action_email.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids,
        'list': emails,  
        'groups': groups,
        'count': ecount,
    }))
 

def action_do_enrollform(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)

    if source_course is None:
        raise Http404



    studs = []
    studs.extend(Student.list_for_course_to_enroll(source_course.key()))
    studs.extend(Student.list_for_course_enrolled(source_course.key()))

    studs = filter(lambda x: str(x.key().id()) in student_ids,studs)
        
    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote((u"prihlasky_%s.pdf"%source_course.code).encode('utf8'))
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_enroll,students_enroll_multi

    students_enroll_multi(r,studs,with_partner=True)
    return r

 

@ar_edit
def action_do_transfer(request, source_course=None, student_ids=None, target_course=None, target_season=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_transfer.html', RequestContext(request, {'info':info}))

    if target_course is None:

        info = 'přeřazení žáků do jiného kurzu'
        if target_season is None:
            filter_form = SeasonFilterForm()
            form = None
        else:
            filter_form = SeasonFilterForm({'season_key':target_season.key()})       
            form = TargetCoursePickForm(courses = target_season.get_COURSE_CHOICES())

        return render_to_response('admin/action_transfer.html', RequestContext(request, {'filter_form': filter_form, 'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))

    job_id=plan_job_transfer_students(request.auth_info.email,student_ids,source_course, target_course)


    return HttpResponseRedirect('../wait/%d/'%job_id)

@ar_edit
def action_do_makecopy(request, source_course=None, student_ids=None, target_course=None, target_season=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_makecopy.html', RequestContext(request, {'info':info}))

    if target_course is None:

        info = 'kopie žáků do jiného kurzu'
        if target_season is None:
            filter_form = SeasonFilterForm()
            form = None
        else:
            filter_form = SeasonFilterForm({'season_key':target_season.key()})       
            form = TargetCoursePickForm(courses = target_season.get_COURSE_CHOICES())


        return render_to_response('admin/action_makecopy.html', RequestContext(request, {'filter_form':filter_form, 'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))

    job_id=plan_job_makecopy_students(request.auth_info.email,student_ids,source_course, target_course)


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

    
@ar_edit
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
  
@ar_edit
def action_do_qcard(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_qcard.html', RequestContext(request, {'info':info}))

    job_id=plan_job_qcard_for_students(request.auth_info.email,student_ids)
    return HttpResponseRedirect('../wait/%d/'%job_id)


    

@ar_edit
def action_do_cardout(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)

    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_cardout.html', RequestContext(request, {'info':info}))

    job_id=plan_job_cardout_for_students(request.auth_info.email,student_ids)
    return HttpResponseRedirect('../wait/%d/'%job_id)

 

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

@ar_edit
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

@ar_edit
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
    s1.mark_as_modify()
    s2.partner_ref_code = s1.ref_key
    s2.mark_as_modify()

    s1.save()
    s2.save()
    cdbsync.plan_cdb_put(s1)
    cdbsync.plan_cdb_put(s2)



    for s in Student.list_by_partner(s1.ref_key):
        if s.key().id != s2.key().id:
            s.partner_ref_code=""
            s.mark_as_modify()
            s.save()
            cdbsync.plan_cdb_put(s)

    
    for s in Student.list_by_partner(s2.ref_key):
        if s.key().id != s1.key().id:
            s.partner_ref_code=""
            s.mark_as_modify()
            s.save()
            cdbsync.plan_cdb_put(s)

 
    return redirect('..')

class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(label='opravdu to chci udělat', error_messages=ERROR_MESSAGES,  required=True)
 

@ar_edit
def action_do_delete(request, source_course=None, student_ids=None):
    logging.info('student_ids = %s'%student_ids)


    if (student_ids is None) or (len(student_ids)==0):
        info = 'nebyl vybrán žádný žák'
        return render_to_response('admin/action_delete.html', RequestContext(request, {'info':info}))

    if not 'confirm' in request.POST:
        form = ConfirmForm()
        info = 'smazaní žáků - celkem %d žáků bude smazáno!'%(len(student_ids))
        return render_to_response('admin/action_delete.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))
   
    form = ConfirmForm(request.POST)
    if form.is_valid():
        confirm = form.cleaned_data['confirm']
        if (confirm):
            job_id=plan_job_hide_students(request.auth_info.email,student_ids, source_course)
            return HttpResponseRedirect('../wait/%d/'%job_id)


    info = 'smazaní žáků' 
    return render_to_response('admin/action_delete.html', RequestContext(request, {'form':form, 'info':info, 'operation':request.POST['operation'], 'all_select':student_ids}))



@ar_edit
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
            student.mark_as_modify()
            student.save()
            cdbsync.plan_cdb_put(student)


            course_id = student.get_course_id()
            logging.info('student course_id = %s'%(course_id))
            plan_update_course(course_id)

            return redirect('../..')
    else:
        form = StudentForm(instance=student)

    return render_to_response('admin/students_edit.html', RequestContext(request, {'form':form}))

@ar_edit
def create(request, course_id):

    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404

    student = Student()
    student.no_email_notification = True
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
            student.init_gid()
            logging.info('create student after %s'% student)
            student.save()
            student.init_ref_codes()
            student.mark_as_modify()
            
            student.save()
            cdbsync.plan_cdb_put(student)

            course_id = student.get_course_id()
            plan_update_course(course_id)

            return redirect('..')
    else:
        form = StudentFormAdd(instance=student)
    return render_to_response('admin/students_create.html', RequestContext(request, {'form':form}))

@ar_edit
def create_pair(request, course_id):

    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404

    student1 = Student()
    student1.no_email_notification = True
    student1.set_course_key(str(course.key()))
    student1.init_reg()
    student1.init_ref_base()
    student1.reg_by_admin = True
    student1.status = '-'
 
    student2 = Student()
    student2.no_email_notification = True
    student2.set_course_key(str(course.key()))
    student2.init_reg()
    student2.init_ref_base()
    student2.reg_by_admin = True
    student2.status = '-'
 
    if request.method == 'POST':
        form1 = StudentFormAdd(request.POST,prefix='p1',instance=student1)
        form2 = StudentFormAdd(request.POST,prefix='p2',instance=student2)

        if form1.is_valid() and form2.is_valid():


            form1.save(commit=False)
            student1.status =  form1.cleaned_data['add_mode']
            if student1.status=='e':
                student1.init_enroll()
            student1.init_gid()
            logging.info('create student after %s'% student1)
            student1.save()
            student1.init_ref_codes()

            form2.save(commit=False)
            student2.status =  form2.cleaned_data['add_mode']
            if student2.status=='e':
                student2.init_enroll()
            student2.init_gid()
            logging.info('create student after %s'% student2)

            student2.save()
            student2.init_ref_codes()


            student1.partner_ref_code = student2.ref_key
            student2.partner_ref_code = student1.ref_key
            
            student1.mark_as_modify()
            student2.mark_as_modify()
            student1.save()
            student2.save()
            cdbsync.plan_cdb_put(student1)
            cdbsync.plan_cdb_put(student2)



            course_id = student1.get_course_id()
            plan_update_course(course_id)

            return redirect('..')

    else:
        form1 = StudentFormAdd(prefix='p1',instance=student1)
        form2 = StudentFormAdd(prefix='p2',instance=student2)

    return render_to_response('admin/students_create_pair.html', RequestContext(request, {'form1':form1,'form2':form2}))

def email(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404
    course = student.get_course()
    partner = student.get_partner()

    emails = []
    for k in mail.MAIL_TEMPLATE_KEYS:
        (subject,body) = mail.prepare_email_text(k, student,course,partner)
        emails.append({'key':k, 'subject':subject, 'body':body}) 

    return render_to_response('admin/students_email.html', RequestContext(request, {
        'emails':emails
    }))

@ar_edit
def enroll(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if (student.status == 's') or (student.status == 'k'):
        student.status = 'e'
        student.mark_as_modify()
        student.init_enroll()
        student.save()
        cdbsync.plan_cdb_put(student)

        plan_send_student_email('ENROLL_OK_PAY_REQUEST', student)
        plan_update_course(course_id)

    return HttpResponseRedirect('../..')
    
@ar_edit
def kick(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if (student.status == 's') or (student.status == 'e'):
        student.status = 'k'
        student.mark_as_modify()
        student.save()
        cdbsync.plan_cdb_put(student)

        plan_send_student_email('ENROLL_KICK', student)
        plan_update_course(course_id)
 
    return HttpResponseRedirect('../..')
 
@ar_edit
def spare(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    if (student.status == 'e') or (student.status == 'k'):
        student.status = 's'
        student.mark_as_modify()
        student.save()
        cdbsync.plan_cdb_put(student)

        plan_send_student_email('ENROLL_KICK_TO_SPARE', student)
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


class PayInfoForm(forms.Form):
    course_cost = forms.IntegerField(label='kurzovné', error_messages=ERROR_MESSAGES)
    paid = forms.IntegerField(label='platba', error_messages=ERROR_MESSAGES)
    discount = forms.CharField(label='sleva', error_messages=ERROR_MESSAGES, required=False)
    pay_info = forms.CharField(label='platební info', error_messages=ERROR_MESSAGES, required=False)
    send_info = forms.BooleanField(label='odeslat info o platbě', error_messages=ERROR_MESSAGES, required=False)

@ar_edit
def pay(request, student_id, course_id=None):
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404
    course = student.get_course()

    
    if request.method == 'POST':
        form = PayInfoForm(request.POST)
        if form.is_valid():
            logging.info('pay student before %s'% student)
            student.course_cost = form.cleaned_data['course_cost']
            student.paid = form.cleaned_data['paid']
            student.discount = form.cleaned_data['discount']
            student.pay_info = form.cleaned_data['pay_info']
            student.mark_as_modify()
            student.save()
            cdbsync.plan_cdb_put(student)
            logging.info('pay student after %s'% student)

            if form.cleaned_data['send_info']:
                logging.info('plan send info email')
                plan_send_student_email('ENROLL_PAY_INFO', student)


            course_id = student.get_course_id()
            logging.info('student course_id = %s'%(course_id))
            plan_update_course(course_id)


            return redirect('../..')
            
    else:
        data = {'course_cost':student.course_cost, 'paid':student.paid, 'discount':student.discount, 'pay_info':student.pay_info,'send_info': (not student.no_email_notification)}
        form = PayInfoForm(data)

    return render_to_response('admin/students_pay.html', RequestContext(request, {
        'student':student,'course':course, 'form':form
    }))

class ChangeQCardForm(forms.Form):
    doit = forms.BooleanField(label='zrušit starou kartu a přidělit nový kód karty', error_messages=ERROR_MESSAGES, required=False)


@ar_edit
def change_qcard(request, student_id, course_id=None):
    student = Student.get_by_id(int(student_id))
    logging.info(student)
    hint = ''
    if student is None:
        raise Http404
    course = student.get_course()
    if request.method == 'POST':
        form = ChangeQCardForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['doit']:
                logging.info("change ref_gid!")

                student.init_gid()
                student.save()
                cdbsync.plan_cdb_put(student)

                return HttpResponseRedirect('../change_qcard_ok/')
        hint = "pro provedení změny je potřeba zašktnout souhlas ve formuláři"
    else:
        data = {'doit': False}
        form = ChangeQCardForm(data)

    return render_to_response('admin/students_change_qcard.html', RequestContext(request, {
        'hint':hint,'student':student,'course':course, 'form':form
    }))

@ar_edit
def change_qcard_ok(request,student_id,course_id=None):
    student = Student.get_by_id(int(student_id))
    logging.info(student)
    if student is None:
        raise Http404
    course = student.get_course()
    return render_to_response('admin/students_change_qcard_ok.html', RequestContext(request, {
        'student':student,'course':course
    }))
  

class EmailSelectForm(forms.Form):
    include_enroll = forms.BooleanField(label='zapsané', error_messages=ERROR_MESSAGES, required=False)
    include_spare = forms.BooleanField(label='náhradníky', error_messages=ERROR_MESSAGES, required=False)
    email_ad = forms.BooleanField(label='i těm co nechtějí reklamy', error_messages=ERROR_MESSAGES, required=False)
    email_info = forms.BooleanField(label='i těm co nechtějí žádné zpravy', error_messages=ERROR_MESSAGES, required=False)
    gsize = forms.IntegerField(label='skupinky po', error_messages=ERROR_MESSAGES,  required=False, initial=40)
 
 

def course_emails(request, course_id):
    course = Course.get_by_id(int(course_id))  
    if course is None:
        raise Http404


    emails = None
    groups = None
    ecount = None
    if request.method == 'POST':
        form = EmailSelectForm(request.POST)
        if form.is_valid():
            studs = []
            if form.cleaned_data['include_spare']:
                studs.extend(Student.list_for_course_to_enroll(course.key()))
            if form.cleaned_data['include_enroll']:
                studs.extend(Student.list_for_course_enrolled(course.key()))
            if not form.cleaned_data['email_ad']:
                studs = filter(lambda x: not x.no_email_ad,studs)
            if not form.cleaned_data['email_info']:
                studs = filter(lambda x: not x.no_email_info,studs)
            if form.cleaned_data['gsize']:
                gsize = form.cleaned_data['gsize']
            else: 
                gsize = 0


            emails = map(attrgetter('email'),studs)
            emails = filter(valid_email,emails)
            emails = sorted(list(set(emails)))
            ecount = len(emails)            
          
            if (gsize) and (gsize>0): 
                groups = chunks(emails,gsize) 
            else:
                groups = [emails]
                

            
    else: 
        form = EmailSelectForm()

    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    return render_to_response('admin/course_emails.html', RequestContext(request, { 
        'course':course,
        'form':form,
        'list': emails,  
        'groups': groups,
        'count': ecount,
    }))

def course_as_csv(request, course_id):
    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404


    r =  HttpResponse(mimetype='application/vnd.ms-excel')
    file_name = urllib.quote((u"kurz_%s.csv"%course.code).encode('utf8'))
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.data import dump_to_csv

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

    students = []
    students.extend(student_list_enrolled)
    students.extend(student_list_to_enroll)

    data = [ ['#export kurz',course.code,course.folder_name(),course.season_name()]]
    for s in students:
        if not s.x_pair_empty_slot:
            data.append(s.as_csv_row())
    dump_to_csv(data,r)
    return r

def student_as_enroll_form(request, course_id, student_id):
    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404


    student = Student.get_by_id(int(student_id))  

    if student is None:
        raise Http404


    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote((u"prihlaska.pdf").encode('utf8'))
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_enroll

    students_enroll(r,[student])

    return r 

def course_as_pdf(request, course_id):

    course = Course.get_by_id(int(course_id))  

    if course is None:
        raise Http404

    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote((u"kurz_%s.pdf"%course.code).encode('utf8'))
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_table

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
    file_name = urllib.quote((u"prihlasky_%s.pdf"%course.code).encode('utf8'))
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
    from utils.pdf import students_enroll,students_enroll_multi

    student_list_to_enroll=Student.list_for_course_to_enroll(course.key())
    student_list_enrolled=Student.list_for_course_enrolled(course.key())

    students = []
    students.extend(student_list_enrolled)
    students.extend(student_list_to_enroll)

    students_enroll_multi(r,students,with_partner=False)
    return r

def qrcmd_cards(request, course_id):
    logging.info("qrcmd cards for course %s" % (course_id))
    course = Course.get_by_id(int(course_id))  

    if course is None:
        logging.info("course not found")
        raise Http404
    logging.info(course)


    if utils.qrg.qrg_cfg_get_on():
        logging.info("qrg is on")
        li = []
        li += [{"cmd_id":"C_SETUP","name":"%s" % course.code, "desc":u"zapne kurz %s" % course.code, "cmd_qrcode": calc_qrcode_for_cmdcard(course,"C_SETUP")}]
        li += [{"cmd_id":"C_SETUP_GM","name":"%s" % course.code, "desc":u"zapne kurz %s (+hostující kluci)" % course.code, "cmd_qrcode": calc_qrcode_for_cmdcard(course,"C_SETUP_GM")}]
        li += [{"cmd_id":"C_ADD","name":"%s" % course.code, "desc":u"povolí hostování všech z kurzu %s" % course.code, "cmd_qrcode": calc_qrcode_for_cmdcard(course,"C_ADD")}]
        li += [{"cmd_id":"C_ADD_M","name":"%s" % course.code, "desc":u"povolí hostování kluků z kurzu %s" % course.code, "cmd_qrcode": calc_qrcode_for_cmdcard(course,"C_ADD_M")}]
        li += [{"cmd_id":"C_ADD_F","name":"%s" % course.code, "desc":u"povolí hostování holek z kurzu %s" % course.code, "cmd_qrcode": calc_qrcode_for_cmdcard(course,"C_ADD_F")}]

        rd = utils.qrg.qrg_post("cmd_cards",li)
        pdfdata = base64.b64decode(rd["data"]) 
        r =  HttpResponse(pdfdata, mimetype='application/pdf')
        file_name = urllib.quote("ovladaci_karty.pdf")
        logging.info(file_name)
        r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name

    else:
        logging.info("qrg is off")
        r =  HttpResponse(mimetype='application/pdf')
        file_name = urllib.quote("ovladaci_karty.pdf")
        logging.info(file_name)
        r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
        pdf.empty_document(r,"ted nelze generovat ovladaci qr karty")

    return r

