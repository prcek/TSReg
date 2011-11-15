# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from utils.data import UnicodeReader
from utils.mail import valid_email
from enroll.models import Course,Student,Folder,Season
from admin.models import FileBlob
from google.appengine.api import taskqueue
import logging
import cStringIO
import datetime
from utils.locale import local_timezone


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


ACTION_CHOICES = (
    ('-','--- zvol akci ---'),
    ('import_students','import žáků'),
)



class UploadFileForm(forms.Form):
    action = forms.CharField(label='akce', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ACTION_CHOICES))
#    post_action_ok = forms.CharField(widget=forms.widgets.HiddenInput())
#    post_action_error = forms.CharField(widget=forms.widgets.HiddenInput())
    file = forms.FileField(label='soubor')


def index(request):

    if request.method == 'POST':
        logging.info(request.POST)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            logging.info('filename="%s", size=%d, content_type="%s" '%(f.name,f.size,f.content_type))
            fb = FileBlob()
            fb.init(f.read(),owner=request.auth_info.email, name=f.name, tmp=True)
            fb.save()
            logging.info('file id=%s'%(fb.key().id()))
            return redirect('%d/%s/'%(fb.key().id(),form.cleaned_data['action']))
    else:
        form = UploadFileForm()


    return render_to_response('admin/import_index.html', RequestContext(request, {  'form': form}))

class TargetPickForm(forms.Form):
    course_key = forms.ChoiceField(label='Do kurzu')
    start_line = forms.IntegerField(widget=forms.widgets.HiddenInput())
    end_line = forms.IntegerField(widget=forms.widgets.HiddenInput())
    def __init__(self, data = None, courses = [], **kwds):
        super(self.__class__,self).__init__(data, **kwds)
        self.fields['course_key'].choices=courses


def import_students(request,file_id, seq_id=None):

    f = FileBlob.get_by_id(int(file_id))

    if f is None:
        raise Http404

    d = cStringIO.StringIO(f.data)
    r = UnicodeReader(d)
   
    form = None
    course = None 
    
    season = None
    cskey = request.session.get('course_season_key',None)
    if not cskey is None:
        season =  Season.get(str(cskey))
    folder = None
    cfkey = request.session.get('course_folder_key',None)
    if not cfkey is None:
        folder =  Folder.get(str(cfkey))    
    
    logging.info('cfkey %s cskey %s'%(cskey,cfkey))
    logging.info('folder: %s'%folder)
    logging.info('season: %s'%season)
    if folder and season:
        cc = Course.get_COURSE_FILTER_CHOICES(str(season.key()),str(folder.key()))
    else:
        cc = Course.get_COURSE_CHOICES()
    
    
    logging.info('cc:%s'%cc)
    
    if request.method == 'POST':
        form = TargetPickForm(request.POST,courses = cc)
    
    info = []
    seq = 0
    curr = None
    line = 0
    for row in r:
        if len(row)>6 and (row[0].startswith('#export kurz') or row[0].startswith('#zaloha kurz')):
            logging.info(row)
            if not curr is None:
                curr["end_line"]=line
                info.append(curr)
            curr = dict()
            curr["seq"]=seq
            seq+=1
            curr["start_line"]=line+1
            curr["code"]=row[1]
            curr["folder"]=row[2]
            curr["season"]=row[3]
            curr["students"]=0
            curr["info"]=row[6]
        elif len(row)>19 and not row[0].startswith('#'):
            curr["students"]+=1
        line+=1 

    if not curr is None:
        curr["end_line"]=line
        info.append(curr)

    selected = None
    if not seq_id is None:
        for c in info:
            if c["seq"]==int(seq_id):
                selected = c 
                break
        
        if selected is None:
            raise Http404

        if form is None: 
            form = TargetPickForm(courses = cc, initial={'start_line':selected['start_line'], 'end_line':selected['end_line']})
        else:
            if form.is_valid():
                course = Course.get(form.cleaned_data['course_key'])
                if course is None:
                    raise Http404
                

    return render_to_response('admin/import_students.html', RequestContext(request, {  'info': info, 'form':form, 'selected':selected, 'course':course, 'season':season, 'folder':folder}))


def import_students_do(request,file_id, start_line, end_line, course_id):

    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    f = FileBlob.get_by_id(int(file_id))
    if f is None:
        raise Http404
    d = cStringIO.StringIO(f.data)
    r = UnicodeReader(d)

    start_line = int(start_line)
    end_line = int(end_line)
    line = 0
    st_list=[]
    for row in r:
        if (line>=end_line):
            break
        if (line>=start_line):
            st = import_student(course,row)
            st_list.append(st)
        line+=1

    if course.group_mode == 'Pair':
        pd = dict()  
        for s in st_list:
            if not s.x_import_no_2 is None:
                p = pd.pop(s.x_import_no_2,None)        
                if p is None:
                    pd[s.x_import_no_2] = s
                else:
                    s.partner_ref_code = p.ref_key
                    p.partner_ref_code = s.ref_key
                    s.save()
                    p.save()

    ###
    taskqueue.add(url='/task/recount_capacity/', params={'course_id':course.key().id()})

    return HttpResponseRedirect('../../../../../')

def AnoNe2Bool(s):
    if s == 'Ano':
        return True
    if s == 'Ne':
        return False
    return None

def import_student(course,row):
    logging.info('import student data=%s'%(row))

    st = Student()
    st.status = 'e'
    st.course_key=str(course.key())
    st.init_reg()
    st.init_ref_base()
    s = row[2].lower()
    if s in ['p','s','d']:
        st.addressing = s
    
#    st.addressing = form.cleaned_data['addressing']
    st.name = row[4]
    st.surname = row[3]


    try:
        st.x_import_no_1 = int(row[0])
    except:
        pass
    try:
        st.x_import_no_2 = int(row[1])
    except:
        pass

# 5 6 7 - prachy

    try:
        paid = int(row[5])
    except:
        paid = 0
    try:
        to_pay = int(row[6])
    except:
        to_pay = 0
        
    st.course_cost = paid+to_pay
    st.paid = paid
        
    st.discount = row[7]
    logging.info('sleva: %s'%st.discount)    

# 8,9 skola  trida
    st.school = row[8]
    st.school_class = row[9]

    st.student = AnoNe2Bool(row[17])
    st.student_check = AnoNe2Bool(row[18])
    
#    st.long_period = form.cleaned_data['long_period']
#    st.year = form.cleaned_data['year']
    st.email = row[15]
    spam = AnoNe2Bool(row[16])
    if spam is True:
        st.no_email_ad = False
    else:
        st.no_email_ad = True

    st.no_email_notification = True
    st.no_email_info = not valid_email(st.email)
    if st.no_email_info:
        st.no_email_ad = True
    st.phone = row[14]
    st.street = row[10]
    st.street_no = row[11]
    st.city = row[12]
    st.post_code = row[13]

    st.comment = row[19]

    st.save()
    st.init_ref_codes()
    st.save()

    return st

