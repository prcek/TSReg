# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
import utils.mail as mail
from admin.models import EMailTemplate
from admin.queue import plan_send_multimail
from google.appengine.api.mail import EmailMessage
from admin.email_views import EMailListField, EMailListWidget
from admin.queue import plan_send_multimail
import re
import sys
import logging


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


class EMailTemplateForm(forms.ModelForm):
    name = forms.CharField(label='název')
    desc = forms.CharField(label='popis',required=False)
    locked = forms.BooleanField(label='zámek', required=False)
    class Meta:
        model = EMailTemplate
        fields = ( 'name','desc','locked' )

def index(request):
    ets = EMailTemplate.list_all()
    return render_to_response('admin/emailtemplate_index.html', RequestContext(request, { 'list': ets  }))

def show(request, et_id):
    et = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404

    return render_to_response('admin/emailtemplate_show.html', RequestContext(request, { 'et': et  }))


def create(request):
    if request.method == 'POST':
        form = EMailTemplateForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            el  = form.save(commit=False)
            el.save()
            logging.info('new el created - %s' % (el))
            return redirect('..')
    else:
        form = EMailTemplateForm() 
    return render_to_response('admin/emailtemplate_create.html', RequestContext(request, { 'form': form }))

def edit(request, et_id):
    et = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404
    if request.method == 'POST':
        form = EMailTemplateForm(request.POST, instance=et)
        if form.is_valid():
            logging.info('edit el before - %s' % (et))
            form.save(commit=False)
            logging.info('edit el after - %s' % (et))
            et.save()
            return redirect('../..')
    else:
        form = EMailTemplateForm(instance=et)
    return render_to_response('admin/emailtemplate_edit.html', RequestContext(request, { 'form': form }) ) 


def delete(request, et_id):

    et  = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404

    et.delete()
    return redirect('../..')

class EMailTestForm(forms.Form):
    email = forms.EmailField(label='email', error_messages=ERROR_MESSAGES )
 
def test_send(request, et_id):
    et  = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404

    if request.method == 'POST':
        form = EMailTestForm(request.POST)
        if form.is_valid():
            try:
                email = EmailMessage(et.data)

                email.sender = cfg.getConfigString('ENROLL_EMAIL',None)
                email.reply_to = cfg.getConfigString('ENROLL_REPLY_TO',None)
                email.to = form.cleaned_data['email']
                email.check_initialized()

                logging.info('sending...')
                email.send()
                logging.info('send ok')

                et.valid = True 
                et.save()

            except:
                logging.info("can't init/send email! %s"%sys.exc_info()[1])
                return HttpResponse("can't init/send email - %s"%sys.exc_info()[1])


            return redirect('../..')
    else:
        form = EMailTestForm()
 
    return render_to_response('admin/emailtemplate_testsend.html', RequestContext(request, { 'form': form, 'et':et }) ) 

class EMailMultiForm(forms.Form):
    emails = EMailListField(widget=EMailListWidget(attrs={'cols':160, 'rows':20}), required=False, label="emaily")
 
def multi_send(request, et_id):
    et  = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404
    
    if not et.valid:
        raise Http404
        

    if request.method == 'POST':
        form = EMailMultiForm(request.POST)
        if form.is_valid():
            el = form.cleaned_data['emails']
            els = list(el.split())
            els_c = len(els)
           
            logging.info('list size %d'%(els_c))
            if els_c > 0: 
                plan_send_multimail(els,et_id)
                return redirect('../..')
    else:
        form = EMailMultiForm()
 
    return render_to_response('admin/emailtemplate_multisend.html', RequestContext(request, { 'form': form, 'et':et }) ) 

