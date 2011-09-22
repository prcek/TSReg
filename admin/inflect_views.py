# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from google.appengine.ext import db

from admin.models import Inflect
import utils.config as cfg
import utils.pdf as pdf
import logging
import urllib


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}

GENDER_CHOICES = (
    ('-','?'),
    ('m','mužský'),
    ('f','ženský'),
)

PART_CHOICES = (
    ('-','?'),
    ('name','jméno'),
    ('surname','přijmení')
)



class InflectForm(forms.ModelForm):

    part = forms.CharField(label='část', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=PART_CHOICES))
    gender = forms.CharField(label='rod', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=GENDER_CHOICES))

    pattern = forms.CharField(label='vzor', error_messages=ERROR_MESSAGES, required=True)
    proposal = forms.CharField(label='návrh 2. pád', error_messages=ERROR_MESSAGES, required=True)


    class Meta:
        model = Inflect
        fields = ( 'part','gender', 'pattern', 'proposal' )


def index(request):
    inflect_list=Inflect.list()

    return render_to_response('admin/inflects_index.html', RequestContext(request, { 'inflect_list': inflect_list }))
    
def edit(request, inflect_id):

    inflect = Inflect.get_by_id(int(inflect_id))

    if inflect is None:
        raise Http404

    if request.method == 'POST':
        form = InflectForm(request.POST, instance=inflect)
        if form.is_valid():
            logging.info('edit inflect before %s'% inflect)
            form.save(commit=False)
            logging.info('edit inflect after %s'% inflect)
            inflect.save()
            return HttpResponseRedirect('../..')
    else:
        form = InflectForm(instance=inflect)

    return render_to_response('admin/inflects_edit.html', RequestContext(request, {'form':form}))

def create(request):

    inflect = Inflect()
    inflect.init(owner=request.auth_info.email)
    if request.method == 'POST':
        form = InflectForm(request.POST, instance=inflect)
        if form.is_valid():
            logging.info('edit inflect before %s'% inflect)
            form.save(commit=False)
            logging.info('edit inflect after %s'% inflect)
            inflect.save()
            return HttpResponseRedirect('..')
    else:
        form = InflectForm(instance=inflect)

    return render_to_response('admin/inflects_create.html', RequestContext(request, {'form':form}))



def delete(request, inflect_id):


    inflect = Inflect.get_by_id(int(inflect_id))

    if inflect is None:
        raise Http404

    inflect.delete()

    return HttpResponseRedirect('../..')

def clear_all(request):
    if not request.auth_info.admin:
        raise Http404
    inflect_keys=Inflect.keys_all()
    logging.info('clear all inflect patterns %s'%inflect_keys)
    db.delete(inflect_keys)

    return HttpResponseRedirect('..')



def setup(request):
    if not request.auth_info.admin:
        raise Http404
    
    from admin.inflect_data import INFLECT_PATTERNS

    for p in INFLECT_PATTERNS:
        logging.info('p=%s',p)
        inflect = Inflect() 
        inflect.init(owner=request.auth_info.email,gender=p[1],part=p[0],pattern=p[2],proposal=p[3])
        inflect.save()

    return HttpResponse('ok')


def test(request):
    
    return HttpResponse('ok')

