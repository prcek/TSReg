# -*- coding: utf-8 -*-


from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Folder,Course,Student
from enroll.views import get_offer_list2
from utils import captcha
from utils import config

import logging
import os


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


def index(request):

    offer = get_offer_list2()
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None


    if 'enable' in request.GET:
    	config.setConfigBool('ENROLL_ENROLL_ON',True)
    if 'disable' in request.GET:
    	config.setConfigBool('ENROLL_ENROLL_ON',False)


    enroll_on =  config.getConfigBool('ENROLL_ENROLL_ON',False)

    return render_to_response('admin/enroll_index.html', RequestContext(request, { 'offer':offer , 'preview':True, 'enroll_on':enroll_on}))

class ConfirmForm(forms.Form):
    ref_code = forms.CharField(label='referenční kód', error_messages=ERROR_MESSAGES,required=False)
    confirm_code = forms.CharField(label='potvrzovací kód', error_messages=ERROR_MESSAGES,required=False)
    
def manual_confirm(request):

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = ConfirmForm()
    return render_to_response('admin/enroll_manual_confirm.html', RequestContext(request, { 'form':form }))
    
