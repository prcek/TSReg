# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging

def index(request):
    cfg_list=cfg.getConfigList()
    return render_to_response('admin/sys_index.html', RequestContext(request, { 'config_list': cfg_list }))

def config_create(request):
    if request.method == 'POST':
        form = cfg.ConfigForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            config  = form.save(commit=False)
            config.save()
            logging.info('new config created - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            return redirect('/admin/sys/')
    else:
        form = cfg.ConfigForm()
    return render_to_response('admin/sys_config_create.html', RequestContext(request, { 'form': form }))

def config_edit(request, config_id):
    config = cfg.Config.get_by_id(int(config_id))
    if config is None:
        raise Http404
    if request.method == 'POST':
        form = cfg.ConfigForm(request.POST, instance=config)
        if form.is_valid():
            logging.info('edit config before - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            form.save(commit=False)
            logging.info('edit config after - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            config.save()
            return redirect('/admin/sys/')
    else:
        form = cfg.ConfigForm(instance=config)
    return render_to_response('admin/sys_config_edit.html', RequestContext(request, { 'form': form }) )

def config_setup(request):
    cfg.setupConfig()
    return redirect('/admin/sys/')
