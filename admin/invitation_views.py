# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from google.appengine.ext import db

from admin.models import Invitation
import utils.config as cfg
import utils.pdf as pdf
import logging
import urllib


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}

SEX_CHOICES = (
    ('-','?'),
    ('m','mužský'),
    ('f','ženský'),
)

MODE_CHOICES = (
    ('direct','přímá'),
    ('parents','rodičům')
)



class InvitationForm(forms.ModelForm):

    mode  = forms.CharField(label='režim adresy', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=MODE_CHOICES))

    name = forms.CharField(label='jméno', error_messages=ERROR_MESSAGES, required=False)
    surname = forms.CharField(label='přijmení', error_messages=ERROR_MESSAGES, required=False)
    street = forms.CharField(label='ulice', error_messages=ERROR_MESSAGES, required=False)
    street_no = forms.CharField(label='číslo', error_messages=ERROR_MESSAGES, required=False)
    city = forms.CharField(label='město', error_messages=ERROR_MESSAGES, required=False)
    post_code= forms.CharField(label='psč', error_messages=ERROR_MESSAGES, required=False)

      
    addressing = forms.CharField(label='oslovení', error_messages=ERROR_MESSAGES, required=False)
    sex  = forms.CharField(label='rod', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=SEX_CHOICES))
    name_inflected = forms.CharField(label='2. pád jména', error_messages=ERROR_MESSAGES, required=False)
    surname_inflected= forms.CharField(label='2. pád přijmení', error_messages=ERROR_MESSAGES, required=False)


    class Meta:
        model = Invitation
        fields = ( 'name','surname', 'street', 'street_no', 'city', 'post_code', 'mode', 'sex', 'addressing', 'name_inflected', 'surname_inflected')


def index(request):
    if (request.auth_info.admin):
        invitation_list=Invitation.list_all()
    else:
        invitation_list=Invitation.list_my(request.auth_info.email)

    return render_to_response('admin/invitations_index.html', RequestContext(request, { 'invitation_list': invitation_list }))
    
def edit(request, invitation_id):

    invitation = Invitation.get_by_id(int(invitation_id))

    if invitation is None:
        raise Http404

    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=invitation)
        if form.is_valid():
            logging.info('edit invitation before %s'% invitation)
            form.save(commit=False)
            logging.info('edit invitation after %s'% invitation)
            invitation.save()
            return HttpResponseRedirect('../..')
    else:
        form = InvitationForm(instance=invitation)

    return render_to_response('admin/invitations_edit.html', RequestContext(request, {'form':form}))

def create(request):

    invitation = Invitation()
    invitation.init(owner=request.auth_info.email)
    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=invitation)
        if form.is_valid():
            logging.info('edit invitation before %s'% invitation)
            form.save(commit=False)
            logging.info('edit invitation after %s'% invitation)
            invitation.save()
            return HttpResponseRedirect('..')
    else:
        form = InvitationForm(instance=invitation)

    return render_to_response('admin/invitations_create.html', RequestContext(request, {'form':form}))



def delete(request, invitation_id):


    invitation = Invitation.get_by_id(int(invitation_id))

    if invitation is None:
        raise Http404

    invitation.delete()

    return HttpResponseRedirect('../..')


def clear_all(request):
    invitation_keys=Invitation.keys_my(request.auth_info.email)
    db.delete(invitation_keys)

    return HttpResponseRedirect('..')

def clear_all_all(request):
    if not request.auth_info.admin:
        raise Http404

    invitation_keys=Invitation.keys_all()

    db.delete(invitation_keys)

    return HttpResponseRedirect('..')


def print_all(request):

    r =  HttpResponse(mimetype='application/pdf')
    file_name = urllib.quote("adresy.pdf")
    logging.info(file_name)
    r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name

    invitation_list=Invitation.list_my(request.auth_info.email)

    mode = request.GET.get('mode',None)

    pdf.students_invitation(r,invitation_list,mode=mode)

    return r

