# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response,  get_object_or_404
from django.template import RequestContext,Context, loader

from wtforms.ext.appengine.db import model_form
from utils.wtf import InputRequired

from google.appengine.api import taskqueue


from enroll.models import Folder,rebuild_folders
import utils.config as cfg
import logging



FolderForm = model_form(Folder, only=['order_value','name', 'public_name'], field_args = {
        'order_value' : { 'label':u'řazení', 'validators':[InputRequired()], 'description':u'kategorie budou tříděny podle tohodle čísla v zestupném pořadí'},
        'name': { 'label':u'název', 'validators':[InputRequired()]},
        'public_name': { 'label': u'veřejný název', 'validators':[InputRequired()]}
    })



def index(request):
    rebuild_folders() 
    folder_list=Folder.list()

    return render_to_response('admin/folders_index.html', RequestContext(request, { 'folder_list': folder_list }))



def edit(request, folder_id):

    folder  = Folder.get_by_id(int(folder_id))
    if folder is None:
        raise Http404

    if request.method == 'POST':
        form = FolderForm(request.POST, obj=folder)
        if form.validate():
            logging.info('edit folder before %s'% folder)
            form.populate_obj(folder)
            logging.info('edit folder after %s'% folder)
            folder.put()
            rebuild_folders()
            return HttpResponseRedirect('../..')
    else:
        form = FolderForm(obj=folder)

    return render_to_response('admin/folders_edit.html', RequestContext(request, {'form':form}))

def create(request):

    folder = Folder()
    if request.method == 'POST':
        form = FolderForm(request.POST, obj=folder)
        if form.validate():
            logging.info('edit folder before %s'% folder)
            form.populate_obj(folder)
            logging.info('edit folder after %s'% folder)
            folder.put()
            rebuild_folders() 
            return HttpResponseRedirect('..')
    else:
        form = FolderForm(obj=folder)
    return render_to_response('admin/folders_create.html', RequestContext(request, {'form':form}))


def delete(request, folder_id):

    folder  = Folder.get_by_id(int(folder_id))
    if folder is None:
        raise Http404

    folder.delete()
    rebuild_folders() 
    return HttpResponseRedirect('../..')



def setup(request):
    if not request.auth_info.admin:
        raise Http404
    
    from utils.setup_data import FOLDERS

    for p in FOLDERS:
        folder = Folder() 
        folder.order_value = p[0]
        folder.name = p[1]
        folder.public_name = p[2] 
        folder.put()

    rebuild_folders()

    return HttpResponseRedirect('..')




