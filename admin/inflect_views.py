# -*- coding: utf-8 -*-

#from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
from wtforms.form import Form
from wtforms.fields import SelectField, TextField
from utils.wtf  import DisabledTextField, InputRequired


from admin.models import Inflect
import utils.config as cfg
import utils.pdf as pdf
import admin.inflector as inflector
import logging
import urllib



#ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}

GENDER_CHOICES = (
    ('-',u'?'),
    ('m',u'mužský'),
    ('f',u'ženský'),
)

PART_CHOICES = [
    ('-',u'?'),
    ('name',u'jméno'),
    ('surname',u'přijmení')
]

InflectForm = model_form(Inflect, only=['part','gender', 'pattern', 'proposal'], field_args = {
        'part' : { 'label':u'část', 'choices':PART_CHOICES},
        'gender': { 'label':u'rod', 'choices':GENDER_CHOICES},
        'pattern': { 'label': u'vzor'},
        'proposal': { 'label': u'návrh 2. pád', 'validators':[InputRequired()]}
    })


class TestInflectForm(Form):

    part = SelectField(label=u'část', choices=PART_CHOICES)
    gender = SelectField(label=u'rod', choices=GENDER_CHOICES)
    pattern = TextField(label=u'1. pád', validators=[InputRequired()])
    proposal = DisabledTextField(label=u'návrh 2. pád')



def index(request):
    inflect_list=Inflect.list()

    return render_to_response('admin/inflects_index.html', RequestContext(request, { 'inflect_list': inflect_list }))

@db.transactional    
def edit(request, inflect_id):

    inflect = Inflect.get_by_id(int(inflect_id))

    if inflect is None:
        raise Http404

    if request.method == 'POST':
        form = InflectForm(request.POST,obj=inflect)
        if form.validate():
            logging.info('edit inflect before %s'% inflect)
            form.populate_obj(inflect)
            logging.info('edit inflect after %s'% inflect)
            inflect.put()
            return HttpResponseRedirect('../..')
    else:
        form = InflectForm(obj=inflect)

    return render_to_response('admin/inflects_edit.html', RequestContext(request, {'form':form}))

@db.transactional    
def create(request):

    inflect = Inflect()
    inflect.init(owner=request.auth_info.email)
    if request.method == 'POST':
        form = InflectForm(request.POST, obj=inflect)
        if form.validate():
            logging.info('edit inflect before %s'% inflect)
            form.populate_obj(inflect)
            logging.info('edit inflect after %s'% inflect)
            inflect.put()
            return HttpResponseRedirect('..')
    else:
        form = InflectForm(obj=inflect)

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
    
    from utils.setup_data import INFLECT_PATTERNS

    for p in INFLECT_PATTERNS:
        inflect = Inflect() 
        inflect.init(owner=request.auth_info.email,gender=p[1],part=p[0],pattern=p[2],proposal=p[3])
        inflect.save()

    return HttpResponseRedirect('..')


def test(request):
    inflector.init_dicts()
    if request.method == 'POST':
        form = TestInflectForm(request.POST)
        if form.validate():
            pattern = form.data['pattern']
            part = form.data['part']
            gender = form.data['gender']

            proposal = inflector.do_inflect(part,gender,pattern)
    
            form = TestInflectForm(**{'proposal':proposal,'pattern':pattern,'gender':gender,'part':part})
            
    else:
        form = TestInflectForm()

    return render_to_response('admin/inflects_test.html', RequestContext(request, {'form':form}))

