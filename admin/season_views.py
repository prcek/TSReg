# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from google.appengine.api import taskqueue


from enroll.models import Season
import utils.config as cfg
import logging


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}


class SeasonForm(forms.ModelForm):
    order_value = forms.IntegerField(label='řazení',error_messages=ERROR_MESSAGES, help_text='sezóny budou tříděny podle tohodle čísla v zestupném pořadí')
    name = forms.CharField(label='název', error_messages=ERROR_MESSAGES)
    public_name = forms.CharField(label='veřejný název', error_messages=ERROR_MESSAGES)


    class Meta:
        model = Season
        fields = ( 'order_value', 'name', 'public_name' )


def index(request):
    season_list=Season.list()

    return render_to_response('admin/seasons_index.html', RequestContext(request, { 'season_list': season_list }))



def edit(request, season_id):

    season  = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            logging.info('edit season before %s'% season)
            form.save(commit=False)
            logging.info('edit season after %s'% season)
            season.save()
            return redirect('../..')
    else:
        form = SeasonForm(instance=season)

    return render_to_response('admin/seasons_edit.html', RequestContext(request, {'form':form}))

def create(request):

    season = Season()
    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            logging.info('edit season before %s'% season)
            form.save(commit=False)
            logging.info('edit season after %s'% season)
            season.save()
            return redirect('..')
    else:
        form = SeasonForm(instance=season)
    return render_to_response('admin/seasons_create.html', RequestContext(request, {'form':form}))


def delete(request, season_id):

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    season.delete()
    return redirect('../..')



