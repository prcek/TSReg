# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from admin.models import AppUser
import logging


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}

class AppUserForm(forms.ModelForm):
    active = forms.BooleanField(label='aktivní', required=False)
    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES)
    email = forms.EmailField(label='email (ID)', error_messages=ERROR_MESSAGES)
    edit = forms.BooleanField(label='právo editace', required=False)
    pay = forms.BooleanField(label='právo platby', required=False)
    power = forms.BooleanField(label='právo power', required=False)
    class Meta:
        model = AppUser
        fields = ( 'active', 'name','email','edit','pay','power' )


def index(request):
    aus = AppUser.list_all()
    return render_to_response('admin/appuser_index.html', RequestContext(request, { 'list': aus  }))

def create(request):
    if request.method == 'POST':
        form = AppUserForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            user  = form.save(commit=False)
            user.save()
            logging.info('new user created - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            return redirect('..')
    else:
        form = AppUserForm() 
    return render_to_response('admin/appuser_create.html', RequestContext(request, { 'form': form }))

def edit(request, user_id):
    user = AppUser.get_by_id(int(user_id))
    if user is None:
        raise Http404
    if request.method == 'POST':
        form = AppUserForm(request.POST, instance=user)
        if form.is_valid():
            logging.info('edit user before - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            form.save(commit=False)
            logging.info('edit user after - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            user.save()
            return redirect('../..')
    else:
        form = AppUserForm(instance=user)
    return render_to_response('admin/appuser_edit.html', RequestContext(request, { 'form': form }) ) 


def flush(request):
    AppUser.flush_auth_dict()
    return redirect('..')


def delete(request, user_id):

    user  = AppUser.get_by_id(int(user_id))
    if user is None:
        raise Http404

    user.delete()
    return redirect('../..')


