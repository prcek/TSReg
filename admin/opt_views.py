# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from django import forms
import utils.config as cfg

import logging



class TextForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols':160, 'rows':20}))

class StringForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(required=True )


class BoolForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput)
    opt = forms.BooleanField(required=False)


def index(request):



   # items = {'t_check_email':None, 't_confirm_email':None, 'b_enroll_on':None }
    items = {}
    keys = [
        'b_enroll_on',
        's_check_email_subject', 
        't_check_email_body',
        's_confirm_email_subject',
        't_confirm_email_body',
        's_enroll_yes_email_subject',
        't_enroll_yes_email_body',
        's_enroll_no_email_subject',
        't_enroll_no_email_body'
     ]
    labels = {
        'b_enroll_on':'globální povolení zápisu',
        's_check_email_subject':'předmět ověřovacího emailu',
        't_check_email_body':'ověřovací email',

        's_confirm_email_subject':'předmět potvrzovací email',
        't_confirm_email_body':'potvrzovací email',

        's_enroll_yes_email_subject':'předmět přijímací email',
        't_enroll_yes_email_body':'přijímací email',

        's_enroll_no_email_subject':'předmět odmítací email',
        't_enroll_no_email_body':'odmítací email',
         }

    if request.method == 'POST':
        logging.info(request.POST)
        k = request.POST['action'] 
        logging.info('action=%s',k)
        if k in keys:
            cfg_name = 'ENROLL_' + k[2:].upper()
            if k.startswith('t'):
                items[k] = TextForm(request.POST)
                items[k].fields['action'].label = labels[k]
                if items[k].is_valid():
                    cfg.setConfigString(cfg_name,items[k].cleaned_data['text'])
            if k.startswith('s'):
                items[k] = StringForm(request.POST)
                items[k].fields['action'].label = labels[k]
                if items[k].is_valid():
                    cfg.setConfigString(cfg_name,items[k].cleaned_data['text'])
            elif k.startswith('b'):
                items[k] = BoolForm(request.POST)
                items[k].fields['action'].label = labels[k]
                if items[k].is_valid():
                    cfg.setConfigBool(cfg_name,items[k].cleaned_data['opt'])
    
            
    


    logging.info("items: %s"%items)    
    for k in keys:
        if not (k in items):
            cfg_name = 'ENROLL_' + k[2:].upper()
            if k.startswith('t'):
                v=cfg.getConfigString(cfg_name,None)
                items[k] = TextForm(data={'text':v,'action':k})
                items[k].fields['action'].label = labels[k]
            if k.startswith('s'):
                v=cfg.getConfigString(cfg_name,None)
                items[k] = StringForm(data={'text':v,'action':k})
                items[k].fields['action'].label = labels[k]
            elif k.startswith('b'):
                v=cfg.getConfigBool(cfg_name,False)
                items[k] = BoolForm(data={'opt':v, 'action':k})
                items[k].fields['action'].label = labels[k]
        else:
            pass
   
    logging.info("items: %s"%items)    
    forms = [ items[k] for k in keys]

    return render_to_response('admin/opt_index.html', RequestContext(request, {'forms':forms}))

