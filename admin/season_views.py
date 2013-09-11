# -*- coding: utf-8 -*-

#from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Context, loader

from wtforms.ext.appengine.db import model_form
from utils.wtf import InputRequired


from google.appengine.api import taskqueue


from enroll.models import Season,rebuild_seasons
import utils.config as cfg
import logging


SeasonForm = model_form(Season, only=['order_value','name', 'public_name'], field_args = {
        'order_value' : { 'label':u'řazení', 'validators':[InputRequired()], 'description':u'sezóny budou tříděny podle tohodle čísla v zestupném pořadí'},
        'name': { 'label':u'název', 'validators':[InputRequired()]},
        'public_name': { 'label': u'veřejný název', 'validators':[InputRequired()]}
    })


def index(request):
    rebuild_seasons()
    season_list=Season.list()

    return render_to_response('admin/seasons_index.html', RequestContext(request, { 'season_list': season_list }))



def edit(request, season_id):

    season  = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    if request.method == 'POST':
        form = SeasonForm(request.POST, obj=season)
        if form.validate():
            logging.info('edit season before %s'% season)
            form.populate_obj(season)
            logging.info('edit season after %s'% season)
            season.put()
            rebuild_seasons()
            return HttpResponseRedirect('../..')
    else:
        form = SeasonForm(obj=season)

    return render_to_response('admin/seasons_edit.html', RequestContext(request, {'form':form}))

def create(request):

    season = Season()
    if request.method == 'POST':
        form = SeasonForm(request.POST, obj=season)
        if form.validate():
            logging.info('edit season before %s'% season)
            form.populate_obj(season)
            logging.info('edit season after %s'% season)
            season.put()
            rebuild_seasons()
            return HttpResponseRedirect('..')
    else:
        form = SeasonForm(obj=season)
    return render_to_response('admin/seasons_create.html', RequestContext(request, {'form':form}))


def delete(request, season_id):

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    season.delete()
    rebuild_seasons()
    return HttpResponseRedirect('../..')


def setup(request):
    if not request.auth_info.admin:
        raise Http404
    
    from utils.setup_data import SEASONS

    for p in SEASONS:
        season = Season() 
        season.order_value = p[0]
        season.name = p[1]
        season.public_name = p[2] 
        season.put()

    rebuild_seasons()

    return HttpResponseRedirect('..')


