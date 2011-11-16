# -*- coding: utf-8 -*-


from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from enroll.models import Folder,Course,Student
from enroll.views import get_offer_list2
from utils import captcha
from utils import config

import logging
import os




def enroll(request):

    offer = get_offer_list2()
    logging.info('offer=%s'%offer)
    if len(offer) == 0:
        offer = None

    return render_to_response('admin/preview_index.html', RequestContext(request, { 'offer':offer , 'preview':True}))

    
        
