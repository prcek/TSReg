# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader


import logging

def index(request):
    return render_to_response('admin/index.html', RequestContext(request))

def sys_index(request):
    return render_to_response('admin/sys_index.html', RequestContext(request))

