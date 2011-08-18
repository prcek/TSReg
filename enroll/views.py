# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader


import logging

def goto_index(request):
    return redirect('/zapis/')

def index(request):
    return render_to_response('enroll/index.html', RequestContext(request))

