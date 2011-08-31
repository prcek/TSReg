# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from google.appengine.api import taskqueue


from enroll.models import Folder
import utils.config as cfg
import logging


ERROR_MESSAGES={'required': 'Prosím vyplň tuto položku', 'invalid': 'Neplatná hodnota'}


class FolderForm(forms.ModelForm):
    order_value = forms.IntegerField(label='řazení',error_messages=ERROR_MESSAGES, help_text='kategorie budou tříděny podle tohodle čísla v zestupném pořadí')
    name = forms.CharField(label='název', error_messages=ERROR_MESSAGES)
    public_name = forms.CharField(label='veřejný název', error_messages=ERROR_MESSAGES)


    class Meta:
        model = Folder
        fields = ( 'order_value', 'name', 'public_name' )


def index(request):
    folder_list=Folder.list()

    return render_to_response('admin/folders_index.html', RequestContext(request, { 'folder_list': folder_list }))



def edit(request, folder_id):

    folder  = Folder.get_by_id(int(folder_id))
    if folder is None:
        raise Http404

    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            logging.info('edit folder before %s'% folder)
            form.save(commit=False)
            logging.info('edit folder after %s'% folder)
            folder.save()
            return redirect('../..')
    else:
        form = FolderForm(instance=folder)

    return render_to_response('admin/folders_edit.html', RequestContext(request, {'form':form}))

def create(request):

    folder = Folder()
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            logging.info('edit folder before %s'% folder)
            form.save(commit=False)
            logging.info('edit folder after %s'% folder)
            folder.save()
            return redirect('..')
    else:
        form = FolderForm(instance=folder)
    return render_to_response('admin/folders_create.html', RequestContext(request, {'form':form}))


def delete(request, folder_id):

    folder  = Folder.get_by_id(int(folder_id))
    if folder is None:
        raise Http404

    folder.delete()
    return redirect('../..')



