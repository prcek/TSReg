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

        't_email_signature',
        's_check_email_subject', 
        't_check_email_body',

        's_confirm_enroll_email_subject',
        't_confirm_enroll_email_body',
        's_confirm_enroll_and_pay_email_subject',
        't_confirm_enroll_and_pay_email_body',
        's_confirm_spare_email_subject',
        't_confirm_spare_email_body',

        's_notify_transfer_email_subject',
        't_notify_transfer_email_body',

        's_notify_paid_email_subject',
        't_notify_paid_email_body',

        's_notify_cancel_email_subject',
        't_notify_cancel_email_body',
 
        's_notify_spare_email_subject',
        't_notify_spare_email_body',

        's_notify_kick_email_subject',
        't_notify_kick_email_body',


     ]
    labels = {
        'b_enroll_on':'globální povolení zápisu',

        't_email_signature':'patička emailu',
        's_check_email_subject':'předmět ověřovacího emailu',
        't_check_email_body':'ověřovací email',

        's_confirm_enroll_email_subject':'předmět potvrzovací email',
        't_confirm_enroll_email_body':'potvrzovací email',
        's_confirm_enroll_and_pay_email_subject':'předmět potvrzovací email s výzvou k platbě',
        't_confirm_enroll_and_pay_email_body':'potvrzovací email s výzvou k platbě',
        's_confirm_spare_email_subject':'předmět potvrzovací email - náhradník',
        't_confirm_spare_email_body':'potvrzovací email - náhradník',

          
        's_notify_transfer_email_subject':'předmět oznámení o přeřazení',
        't_notify_transfer_email_body':'oznámení o přerazení email',
        
        's_notify_paid_email_subject':'předmět oznámení o zaplacení',
        't_notify_paid_email_body':'oznámení o zaplacení email',
 
        's_notify_cancel_email_subject':'předmět oznámení o zrušení kurzu',
        't_notify_cancel_email_body':'oznámení o zrušení kurzu email',

        's_notify_spare_email_subject':'předmět oznámení o přesunu mezi náhradníky',
        't_notify_spare_email_body':'oznámení o přesunu mezi náhradníky email',

        's_notify_kick_email_subject':'předmět oznámení o vyřazení z kurzu',
        't_notify_kick_email_body':'oznámení o vyřazení z kurzu email',



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

