# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from google.appengine.ext import db

from admin.models import Card
import utils.config as cfg
import utils.pdf as pdf
import logging
import urllib


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}



class CardForm(forms.ModelForm):
    season_name = forms.CharField(label='název sezóny', error_messages=ERROR_MESSAGES, required=False)
    course_code = forms.CharField(label='kód kurzu', error_messages=ERROR_MESSAGES, required=False)
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES, required=False)
    surname = forms.CharField(label='přijmení', error_messages=ERROR_MESSAGES, required=False)
    info_line_1 = forms.CharField(label='1. řádek', error_messages=ERROR_MESSAGES, required=False)
    info_line_2 = forms.CharField(label='2. řádek', error_messages=ERROR_MESSAGES, required=False)

    class Meta:
        model = Card 
        fields = ( 'season_name','course_code', 'name', 'surname', 'info_line_1','info_line_2')


def index(request):
    if (request.auth_info.admin):
        card_list=Card.list_all()
    else:
        card_list=Card.list_my(request.auth_info.email)

    return render_to_response('admin/cards_index.html', RequestContext(request, { 'card_list': card_list }))
    
def edit(request, card_id):

    card = Card.get_by_id(int(card_id))

    if card is None:
        raise Http404

    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            logging.info('edit card before %s'% card)
            form.save(commit=False)
            logging.info('edit card after %s'% card)
            card.save()
            return HttpResponseRedirect('../..')
    else:
        form = CardForm(instance=card)

    return render_to_response('admin/cards_edit.html', RequestContext(request, {'form':form}))

def create(request):

    card = Card()
    card.init(owner=request.auth_info.email)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            logging.info('edit card before %s'% card)
            form.save(commit=False)
            logging.info('edit card after %s'% card)
            card.save()
            return HttpResponseRedirect('..')
    else:
        form = CardForm(instance=card)

    return render_to_response('admin/cards_create.html', RequestContext(request, {'form':form}))



def delete(request, card_id):


    card = Card.get_by_id(int(card_id))

    if card is None:
        raise Http404

    card.delete()

    return HttpResponseRedirect('../..')


def clear_all(request):
    card_keys=Card.keys_my(request.auth_info.email)
    db.delete(card_keys)

    return HttpResponseRedirect('..')

def clear_all_all(request):
    if not request.auth_info.admin:
        raise Http404

    card_keys=Card.keys_all()

    db.delete(card_keys)

    return HttpResponseRedirect('..')


def print_all(request):

    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote("karty.pdf")
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name

    card_list=Card.list_my(request.auth_info.email)

    pdf.students_card(r,card_list)

    return r

