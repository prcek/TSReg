# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Season,Student,Course,FolderStats
from admin.models import Job,Card,QCard,Invitation,CourseBackup,EMailTemplate,EMailJob
from email.utils import parseaddr
import utils.config as cfg
import utils.mail as mail
import files
from google.appengine.api import mail as gmail
from google.appengine.api.mail import EmailMessage
from google.appengine.api import taskqueue
import admin.inflector as inflector

from admin.student_sort import sort_students_single, sort_students_school, sort_students_pair, sort_students_spare_single, sort_students_spare_school, sort_students_spare_pair
from admin.queue import plan_send_student_email, plan_send_multimail, plan_send_mail

import re
from utils.data import dump_to_csv
import utils.cdbsync as cdbsync
from utils.qrcode import calc_qrcode_for_student
import utils.gid_pool as gid_pool
import cStringIO
from google.appengine.ext import db

import logging
import sys


def cdbsync_model(request):
    logging.info("cdbsync_model")
    logging.info(request.POST)
    cdbsync.planned_cdb_put(request.POST['key'])
    return HttpResponse('ok')

def course_fullsync(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404
    cdbsync.plan_cdb_put(course)
    logging.info('course=%s'%course)
    students = Student.list_for_course(course.key())
    for s in students:
        logging.info("student %s" % s.key())
        cdbsync.plan_cdb_put(s)
    logging.info("all done")
    return HttpResponse('ok')

def update_all_folders(request):
    logging.info("update_all_folders")
    logging.info(request.POST)
    folders = Folder.list()
    for f in folders:
        logging.info("folder %s"%f.key())
        cdbsync.plan_cdb_put(f)
    return HttpResponse('ok')

def update_all_students(request):
    logging.info("update_all_students")
    logging.info(request.POST)
    seasons = Season.list()
    for s in seasons:
        logging.info("season %s"%s.key())
        taskqueue.add(url='/task/update_all_students_for_season/', params={'season_id':s.key().id()})
    return HttpResponse('ok')

def update_all_students_for_season(request):
    logging.info("update_all_students_for_season")
    logging.info(request.POST)
    season_id = request.POST['season_id']
    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404
    logging.info("season %s" % season)
    cdbsync.plan_cdb_put(season)
    courses = Course.list_season(str(season.key()))
    logging.info("all courses get")
    for c in courses:
        logging.info("course %s "%c.key())
        taskqueue.add(url='/task/update_all_students_for_course/', params={'course_id':c.key().id()})
    return HttpResponse('ok')

def update_all_students_for_course(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404
    logging.info('course=%s'%course)
    cdbsync.plan_cdb_put(course)
    students = Student.list_for_course(course.key())
    for s in students:
        logging.info("student %s" % s.key())
        taskqueue.add(url='/task/update_all_students_do_one/', params={'student_key':s.key()})

    logging.info("all done")
    return HttpResponse('ok')

def update_all_students_do_one(request):
    logging.info("update_all_students_do_one")
    logging.info(request.POST)
    student_key = request.POST["student_key"]
    s = Student.get(student_key)
    if s is None:
        raise Http404

    logging.info("update student %s"%s)

    cdbsync.plan_cdb_put(s)

    return HttpResponse('ok')





def send_student_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))
    if student is None:
        logging.info('student is None')
        raise Http404
    logging.info('student=%s'%(student))

    course = student.get_course()
    partner = student.get_partner()

    logging.info('course=%s'%(course))

    template_key = request.POST['template_key']
    if template_key is None:
        logging.info('template_key is None')
        raise Http404

    logging.info('template_key=%s'%(template_key))

    if not template_key in mail.MAIL_TEMPLATE_KEYS:
        logging.info('template_key is not valid')
        raise Http404

    logging.info('key ok')

    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    reply_to = cfg.getConfigString('ENROLL_REPLY_TO',None)
    bcc = cfg.getConfigString('ENROLL_BCC',None)


    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')

    if reply_to is None:
        logging.info('no reply to !, skip')
        return HttpResponse('ok')


    if not mail.valid_email(student.email):
        logging.info('no valid student email')
        return HttpResponse('ok')

    recipient = student.email.__str__()

    logging.info('prepare text')
    (subject,body) = mail.prepare_email_text(template_key, student,course,partner)
    logging.info('prepare text done')


#    sss=unicode(body,'utf-8')
#    logging.info(type(subject))
#    logging.info(sss)
#    logging.info(body.encode('utf8'))


    logging.info('sender [%s]'%(sender))
    logging.info('reply_to [%s]'%(sender))
    logging.info('recipient [%s]'%(recipient))
    if not (bcc is None):
        logging.info('bcc [%s]'%(bcc))

    if bcc is None:
        logging.info('no bcc !, ignore bcc header')
        gmail.send_mail(sender=sender, reply_to=reply_to, to=recipient, subject=subject,body=body)
    else:
        gmail.send_mail(sender=sender, reply_to=reply_to, bcc=bcc, to=recipient, subject=subject,body=body)

    logging.info('sent out !')

    return HttpResponse('ok')


def plan_multimail(request):
    logging.info(request.POST)
    recipients = request.POST.getlist('recipients')
    ej_id = request.POST['ej_id']

    if (ej_id is None):
        return HttpResponse('error')

    if (recipients is None) or (len(recipients)==0):
        return HttpResponse('error')
    if len(recipients)==1:
        plan_send_mail(recipients[0],ej_id)
    else:
        sp = len(recipients)/2
        plan_send_multimail(recipients[:sp],ej_id)
        plan_send_multimail(recipients[sp:],ej_id)


    return HttpResponse('ok')

def send_mail(request):
    logging.info(request.POST)
    recipient = request.POST['recipient']
    ej_id = request.POST['ej_id']

    logging.info('fake email to %s'%(recipient))
    logging.info('ej_id %s'%ej_id)



    ej  = EMailJob.get_by_id(int(ej_id))
    if ej is None:
        return HttpResponse('missing ej')

    try:
        email = EmailMessage(ej.data)

        email.sender = cfg.getConfigString('ENROLL_EMAIL',None)
        email.reply_to = cfg.getConfigString('ENROLL_REPLY_TO',None)
        email.to = recipient
        email.check_initialized()

        logging.info('sending...')
        email.send()
        logging.info('send ok')
    except Exception,e:
        logging.info(e)
        logging.info("can't init/send email! %s"%sys.exc_info()[1])
        return HttpResponse("can't init/send email - %s"%sys.exc_info()[1])


    return HttpResponse('ok')

def _obs_send_check_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))

    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_check_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)

    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')

    recipient = student.email.__str__()

    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))

    gmail.send_mail(sender, recipient, subject,body)

    logging.info('send ok')

    return HttpResponse('ok')

def _obs_send_confirm_email(request):
    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))

    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_confirm_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()

    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))

    gmail.send_mail(sender, recipient, subject,body)

    logging.info('send ok')

    return HttpResponse('ok')

def _obs_send_enroll_yes_email(request):

    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))

    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_enroll_yes_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()

    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))

    gmail.send_mail(sender, recipient, subject,body)

    logging.info('send ok')

    return HttpResponse('ok')

def _obs_send_enroll_no_email(request):

    logging.info(request.POST)
    student_id = request.POST['student_id']
    student = Student.get_by_id(int(student_id))

    if student is None:
        raise Http404
    course = student.get_course()

    (subject,body) = mail.prepare_enroll_no_email_text(student,course)
    sender = cfg.getConfigString('ENROLL_EMAIL',None)
    if sender is None:
        logging.info('no sender, skip')
        return HttpResponse('ok')


    recipient = student.email.__str__()

    logging.info('sending from "%s", to "%s", subject "%s", body "%s"'%(sender,recipient,subject,body))

    gmail.send_mail(sender, recipient, subject,body)

    logging.info('send ok')

    return HttpResponse('ok')


def recount_course_capacity(course):

    if course is None:
        raise Http404

    pending = 0
    pending_m = 0
    pending_f = 0
    enrolled = 0
    enrolled_m = 0
    enrolled_f = 0

    unconf = 0
    unconf_m = 0
    unconf_f = 0


    enrolled_paid = 0

    stat_fp_m = 0
    stat_pp_m = 0
    stat_np_m = 0

    stat_fp_f = 0
    stat_pp_f = 0
    stat_np_f = 0


    list = Student.list_for_course(course.key())
    for s in list:
        m = False
        f = False
        if s.addressing == 'p':
            m=True
        elif s.addressing == 's' or s.addressing == 'd':
            f=True

        if s.status == 's':
            pending+=1
            if m:
                pending_m+=1
            if f:
                pending_f+=1
        elif s.status == 'n':
            unconf+=1
            if m:
                unconf_m+=1
            if f:
                unconf_f+=1

        elif s.status == 'e':
            if not s.paid is None:
                enrolled_paid+=s.paid

            enrolled+=1
            if m:
                enrolled_m+=1
            if f:
                enrolled_f+=1

            if s.is_fp():
                if m:
                    stat_fp_m+=1
                if f:
                    stat_fp_f+=1
            elif s.is_pp():
                if m:
                    stat_pp_m+=1
                if f:
                    stat_pp_f+=1
            elif s.is_np():
                if m:
                    stat_np_m+=1
                if f:
                    stat_np_f+=1




    course.pending=pending
    course.usage=enrolled
    course.unconf=unconf

    course.stat_e_m = enrolled_m
    course.stat_s_m = pending_m
    course.stat_e_f = enrolled_f
    course.stat_s_f = pending_f
    course.stat_paid = enrolled_paid

    course.stat_fp_m = stat_fp_m
    course.stat_pp_m = stat_pp_m
    course.stat_np_m = stat_np_m

    course.stat_fp_f = stat_fp_f
    course.stat_pp_f = stat_pp_f
    course.stat_np_f = stat_np_f





    pend_open = True
    if (course.pending_limit!=-1):
        if (course.pending>=course.pending_limit):
            pend_open = False


    cap_open = True
    if (course.capacity!=-1):
        if (course.usage>=course.capacity):
            cap_open = False


    course.suspend = not (cap_open or pend_open)
    course.mark_as_modify()




def recount_capacity(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    recount_course_capacity(course)
    course.save()
    logging.info(course)
    cdbsync.plan_cdb_put(course)


    return HttpResponse('ok')


def hide_course_students(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))

    if course is None:
        raise Http404

    list = Student.list_for_course(course.key())
    for s in list:
        s.hidden = True
        s.save()
        cdbsync.plan_cdb_put(s)


    course.mark_as_modify()
    course.save()
    cdbsync.plan_cdb_put(course)


    return HttpResponse('ok')

def transfer_student(student_id, course):
    logging.info('transfer student %d'%student_id)
    student = Student.get_by_id(student_id)
    if student is None:
        return

    student.set_course_key(str(course.key()))
    student.save()
    cdbsync.plan_cdb_put(student)


    try:
        plan_send_student_email('ENROLL_TRANSFER', student)
    except:
        logging.info('email problem...')



def transfer_students(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()



    student_ids = request.POST.getlist('student_ids')
    target_course_id = request.POST['target_course_id']
    source_course_id = request.POST['source_course_id']



    target_course = Course.get_by_id(int(target_course_id))
    if target_course is None:
        logging.info('missing target course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')

    source_course = Course.get_by_id(int(source_course_id))
    if source_course is None:
        logging.info('missing source course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')



    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        transfer_student(int(student_id), target_course)

    recount_course_capacity(source_course)
    source_course.save()
    logging.info(source_course)
    cdbsync.plan_cdb_put(source_course)



    taskqueue.add(url='/task/recount_capacity/', params={'course_id':target_course.key().id()})


    job.finish()
    job.save()

    return HttpResponse('ok')

def makecopy_student(student_id, course):
    logging.info('makecopy student %d'%student_id)
    student = Student.get_by_id(student_id)
    if student is None:
        return

    new = student.clone()
    logging.info('clone ok')
    new.set_course_key(str(course.key()))
    new.save()
    cdbsync.plan_cdb_put(new)


    return (student.ref_key,new)


def makecopy_students(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()



    student_ids = request.POST.getlist('student_ids')
    target_course_id = request.POST['target_course_id']
    source_course_id = request.POST['source_course_id']



    target_course = Course.get_by_id(int(target_course_id))
    if target_course is None:
        logging.info('missing target course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')

    source_course = Course.get_by_id(int(source_course_id))
    if source_course is None:
        logging.info('missing source course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')



    logging.info('student list %s'%student_ids)
    pr = dict()
    for student_id in student_ids:
        (old_refkey,new) = makecopy_student(int(student_id), target_course)
        pr[old_refkey]=new

    logging.info('stage 2 done')
    for n in pr.values():
        np = pr.get(n.partner_ref_code,None)
        if not np is None:
            logging.info('update partner_ref_code %s -> %s'%(n.partner_ref_code,np.ref_key))
            n.partner_ref_code=np.ref_key
            n.save()
            cdbsync.plan_cdb_put(n)






    taskqueue.add(url='/task/recount_capacity/', params={'course_id':target_course.key().id()})


    job.finish()
    job.save()

    return HttpResponse('ok')


def prepare_card(owner, student_id, season_name, course_code, info_line_1, info_line_2):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return

    card = Card()
    card.init(owner=owner,name=student.name, surname=student.surname, season_name=season_name,  course_code=course_code, info_line_1=info_line_1, info_line_2=info_line_2)
    card.save()
    logging.info('card=%s'%card)

def prepare_cards(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']
    season_name = request.POST['season_name']
    course_code = request.POST['course_code']
    info_line_1 = request.POST['info_line_1']
    info_line_2 = request.POST['info_line_2']


    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        try:
            prepare_card(owner, student_id, season_name, course_code, info_line_1, info_line_2)
        except:
            logging.info("can't prepare card")



    job.finish()
    job.save()

    return HttpResponse('ok')


def prepare_qcard(owner, student_id):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return
    course = student.get_course()
    season = course.get_season()

    logging.info("creating QR card for student %s" % (student))
    logging.info("creating QR card for course %s" % (course))
    logging.info("creating QR card for season %s" % (season))
    qcard = QCard()

    season_name = season.public_name
    course_code = course.code
    info_line_1=course.card_line_1
    info_line_2=course.card_line_2
    qrcode = calc_qrcode_for_student(student,course,season)
    qcard.init(owner=owner,ref_gid=student.ref_gid, name=student.name, surname=student.surname, season_name=season_name,  course_code=course_code, info_line_1=info_line_1, info_line_2=info_line_2, qrcode=qrcode)
    qcard.save()

    logging.info('qcard=%s'%qcard)



def prepare_qcards(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']


    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        try:
            prepare_qcard(owner, student_id)
        except Exception,e:
            logging.info(e)
            logging.info("can't prepare qcard %s" %x)



    job.finish()
    job.save()

    return HttpResponse('ok')

def mark_cardout(owner, student_id):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return

    student.card_out=True
    student.save()
    cdbsync.plan_cdb_put(student)




def prepare_cardout(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']

    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        try:
            mark_cardout(owner, student_id)
        except:
            logging.info("can't prepare card")



    job.finish()
    job.save()

    return HttpResponse('ok')


def prepare_invitation(owner, student_id, mode, addressing_parents, addressing_p, addressing_s, addressing_d):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return


    logging.info('student: %s'%student)

    addressing=''
    iname = None
    isurname = None
    if mode=='parents':
        addressing=addressing_parents
        sex=student.get_sex()
        if not student.name is None:
            iname = inflector.do_inflect('name',sex,student.name)

        if not student.surname is None:
            isurname = inflector.do_inflect('surname',sex,student.surname)

    elif mode=='direct':
        if student.addressing =='p':
            addressing=addressing_p
        elif student.addressing =='s':
            addressing=addressing_s
        elif student.addressing =='d':
            addressing=addressing_d

    logging.info('addressing:%s'%addressing)

    invitation = Invitation()

    invitation.init(owner=owner,mode=mode, addressing=addressing, name=student.name, surname=student.surname, sex=student.get_sex(), street=student.street,
        street_no=student.street_no, city=student.city, post_code=student.post_code
                )

    if not iname is None:
        invitation.name_inflected = iname
    if not isurname is None:
        invitation.surname_inflected = isurname


    logging.info('pre save invitation=%s'%invitation)

    invitation.save()
    logging.info('invitation=%s'%invitation)


def prepare_invitations(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']
    mode = request.POST['mode']
    addressing_parents = request.POST['addressing_parents']
    addressing_p = request.POST['addressing_p']
    addressing_s = request.POST['addressing_s']
    addressing_d = request.POST['addressing_d']


    inflector.init_dicts()


    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        try:
            prepare_invitation(owner, student_id, mode,addressing_parents, addressing_p, addressing_s, addressing_d)
        except:
            logging.info("can't prepare invitation")


    job.finish()
    job.save()

    return HttpResponse('ok')


def hide_student(owner, student_id):
    student = Student.get_by_id(int(student_id))
    if student is None:
        return

    student.hidden = True
    student.save()
    cdbsync.plan_cdb_put(student)




def hide_students(request):
    logging.info(request.POST)
    job_id = request.POST['job_id']
    job = Job.get_by_id(int(job_id))

    job.start()
    job.save()


    student_ids = request.POST.getlist('student_ids')
    owner = request.POST['owner']
    course_id = request.POST['course_id']

    course = Course.get_by_id(int(course_id))
    if course is None:
        logging.info('missing course')
        job.finish(error=True)
        job.save()
        return HttpResponse('error')


    logging.info('student list %s'%student_ids)
    for student_id in student_ids:
        try:
            hide_student(owner, student_id)
        except:
            logging.info("can't hide student")

    recount_course_capacity(course)
    course.save()
    logging.info(course)
    cdbsync.plan_cdb_put(course)



    job.finish()
    job.save()

    return HttpResponse('ok')



def course_backup(request):
    logging.info(request.POST)
    course_id = request.POST['course_id']
    course = Course.get_by_id(int(course_id))
    if course is None:
        raise Http404

    logging.info('course=%s'%course)


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

    data = [ ['#zaloha kurz',course.code,course.folder_name(),course.season_name()]]
    for s in students:
        if not s.x_pair_empty_slot:
            data.append(s.as_csv_row())

    out = cStringIO.StringIO()
    dump_to_csv(data,out)
#    logging.info(out)
    cb = CourseBackup()
    cb.init(out.getvalue(),course=course)
    cb.save()
    course.mark_as_backup()
    course.save()


    if cfg.getConfigBool('BACKUP_EMAIL_ON',False):
        taskqueue.add(url='/task/send_backup/', params={'coursebackup_id':cb.key().id()})
        logging.info('send task plan ok, cbid=%s'%(cb.key().id()))
    else:
        logging.info('BACKUP_EMAIL_ON is OFF!')
    return HttpResponse('ok')

def send_backup(request):

    logging.info(request.POST)


    if not cfg.getConfigBool('BACKUP_EMAIL_ON',False):
        logging.info('BACKUP_EMAIL_ON is OFF!')
        return HttpResponse('ok')

    cb_id = request.POST['coursebackup_id']
    cb = CourseBackup.get_by_id(int(cb_id))
    if cb is None:
        raise Http404

    logging.info('cb=%s'%cb)


    sender = cfg.getConfigString('BACKUP_EMAIL_SENDER',None)
    to = cfg.getConfigString('BACKUP_EMAIL_TO',None)

    if sender is None:
        logging.info('no sender')
        return HttpResponse('ok')

    if to is None:
        logging.info('no to')
        return HttpResponse('ok')

    subject = "Zaloha %s"%(cb.info)
    body = "Zaloha %s, porizeno %s"%(cb.info,cb.create_datetime)

    gmail.send_mail(sender=sender, to=to,subject=subject,body=body,attachments=[(cb.filename,cb.data)])
    logging.info('send ok')


    return HttpResponse('ok')


def send_enroll_form_to_admin(request,test_id=None):
    logging.info(request.POST)

    if not cfg.getConfigBool('ENROLL_FORM_EMAIL_ON',False):
        logging.info('ENROLL_FORM_EMAIL_ON is OFF!')
        return HttpResponse('ok - disabled')


    if test_id is None:
        student_id = request.POST['student_id']
    else:
        student_id = test_id
    student = Student.get_by_id(int(student_id))
    if student is None:
        raise Http404

    logging.info('student=%s'%student)

    course = student.get_course()
    partner = student.get_partner()

    logging.info('course=%s'%(course))

    sender = cfg.getConfigString('ENROLL_FORM_EMAIL_SENDER',None)
    to = cfg.getConfigString('ENROLL_FORM_EMAIL_TO',None)

    if sender is None:
        logging.info('no sender')
        return HttpResponse('ok - no sender, ignore')

    if to is None:
        logging.info('no to')
        return HttpResponse('ok - no to, ignore')


    logging.info('prepare text')
    (subject,body) = mail.prepare_email_text('ENROLL_FORM_REPORT', student,course,partner)
    logging.info('prepare text done')

#    subject =  "online prihlaska" #cfg.getConfigString('ENROLL_FORM_EMAIL_SUBJECT',None)
#    body = "online prihlaska je v priloze" #cfg.getConfigString('ENROLL_FORM_EMAIL_SUBJECT',None)

    filename = "prihlaska.pdf"
    out = cStringIO.StringIO()
    from utils.pdf import students_enroll
    students_enroll(out,[student],with_partner=True)
    data=out.getvalue()

    gmail.send_mail(sender=sender, to=to,subject=subject,body=body,attachments=[(filename,data)])
    logging.info('send ok')


    return HttpResponse('ok')

def process_incoming_email_template(template_id, data):
    logging.info('processing incoming email template')
    et = EMailTemplate.get_by_id(int(template_id))
    if et is None:
        logging.info('template not found')
        return

    if et.locked:
        logging.info('template is locked')
        return

    et.setData(data)

    et.save()

    logging.info('template updated and closed')




def incoming_email(request):
    logging.info(request.POST)
    filename= request.POST['filename']
    logging.info("filename = %s"%(filename))
    data = files.read_file(filename)

    logging.info('email fetch ok')
    email = EmailMessage(data)
    a_to = parseaddr(email.to)[1]
    a_from = parseaddr(email.sender)[1]
    logging.info('email.to=%s'%a_to)
    logging.info('email.sender=%s'%a_from)

    r = re.match(r'^import-email-(\d+)@',a_to)
    if r:
        logging.info('import email, id %s'%r.group(1))
        process_incoming_email_template(r.group(1),data)
        return HttpResponse("ok - import email")

    return HttpResponse('ok - ign')


def update_folder_stats(request):
    logging.info(request.POST)
    folder_key = request.POST['folder_key']
    season_key = request.POST['season_key']

    course_list=Course.list_filter(season_key,folder_key)

    tc_em = 0
    tc_ef = 0
    tc_e = 0
    tc_pm = 0
    tc_pf = 0
    tc_p = 0

    tc_ppm = 0
    tc_ppf = 0
    tc_pp = 0

    tc_npm = 0
    tc_npf = 0
    tc_np = 0

    tc_sum = 0
    if course_list is not None:
        for c in course_list:
            tc_em+=c.stat_e_m
            tc_ef+=c.stat_e_f
            tc_e+=c.usage
            tc_pm+=c.stat_fp_m
            tc_pf+=c.stat_fp_f
            tc_p+=c.stat_fp_m+c.stat_fp_f
            tc_ppm+=c.stat_pp_m
            tc_ppf+=c.stat_pp_f
            tc_pp+=c.stat_pp_m+c.stat_pp_f
            tc_npm+=c.stat_np_m
            tc_npf+=c.stat_np_f
            tc_np+=c.stat_np_m+c.stat_np_f
            tc_sum+=c.stat_paid

    logging.info('stat done')

    fs = FolderStats.get_or_create(season_key,folder_key)

    logging.info('old folder stats %s' % (fs))


    fs.stat_em = tc_em
    fs.stat_ef = tc_ef
    fs.stat_e = tc_e

    fs.stat_pm = tc_pm
    fs.stat_pf = tc_pf
    fs.stat_p = tc_p

    fs.stat_ppm = tc_ppm
    fs.stat_ppf = tc_ppf
    fs.stat_pp = tc_pp

    fs.stat_npm = tc_npm
    fs.stat_npf = tc_npf
    fs.stat_np = tc_np

    fs.stat_sum = tc_sum

    fs.mark_update()
    fs.save()

    logging.info('folder stats %s' % (fs))

    return HttpResponse('ok')
