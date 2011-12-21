# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
import utils.mail as mail
from admin.models import EMailTemplate
from admin.queue import plan_send_multimail
import re
import logging


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


class EMailTemplateForm(forms.ModelForm):
    name = forms.CharField()
    desc = forms.CharField(required=False)
    class Meta:
        model = EMailTemplate
        fields = ( 'name','desc' )

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

def test_send(request, et_id):
    et  = EMailTemplate.get_by_id(int(et_id))
    if et is None:
        raise Http404
#TODO
    return redirect('../..')

