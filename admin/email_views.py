# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from admin.models import EMailList
import logging


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}

class EMailListField(forms.CharField):
    pass

class EMailListForm(forms.ModelForm):
    name = forms.CharField()
    desc = forms.CharField(required=False)
    emails = EMailListField(widget=forms.Textarea(attrs={'cols':160, 'rows':20}), required=False, label="emaily")
    class Meta:
        model = EMailList 
        fields = ( 'name','desc', 'emails' )

def index(request):
    els = EMailList.list_all()
    return render_to_response('admin/email_index.html', RequestContext(request, { 'list': els  }))

def show(request, el_id):
    el = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404
    return render_to_response('admin/email_show.html', RequestContext(request, { 'el': el  }))

def create(request):
    if request.method == 'POST':
        form = EMailListForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            el  = form.save(commit=False)
            el.save()
            logging.info('new el created - %s' % (el))
            return redirect('..')
    else:
        form = EMailListForm() 
    return render_to_response('admin/email_create.html', RequestContext(request, { 'form': form }))

def edit(request, el_id):
    el = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404
    if request.method == 'POST':
        form = EMailListForm(request.POST, instance=el)
        if form.is_valid():
            logging.info('edit el before - %s' % (el))
            form.save(commit=False)
            logging.info('edit el after - %s' % (el))
            el.save()
            return redirect('../..')
    else:
        form = EMailListForm(instance=el)
    return render_to_response('admin/email_edit.html', RequestContext(request, { 'form': form }) ) 


def delete(request, el_id):

    el  = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404

    el.delete()
    return redirect('../..')


