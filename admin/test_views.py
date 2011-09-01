
import sys
if 'libs' not in sys.path:
    sys.path.insert(0,'libs')

from pytz.gae import pytz

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging
import datetime

def index(request):

    tz = pytz.timezone('Europe/Prague') 
   
    now = datetime.datetime.utcnow() 

    logging.info(now)
    logging.info(tz)
    localized_now = tz.localize(now)
    local_now = tz.fromutc(now)
    logging.info(local_now)
    local_s = local_now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(local_s)

    return render_to_response('admin/test.html', RequestContext(request, { 'now': now, 'localized_now': localized_now, 'local_now': local_now, 'local_s': local_s }))

