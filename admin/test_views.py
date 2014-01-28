

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging
import datetime
from utils.locale import local_timezone

def index(request):

    tz = local_timezone #pytz.timezone('Europe/Prague') 
   
    now = datetime.datetime.utcnow() 

    logging.info(now)
    logging.info(tz)
    localized_now = tz.localize(now)
    local_now = tz.fromutc(now)
    logging.info(local_now)
    local_s = local_now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(local_s)

    lines = []
    for i in range(10):
        lines.append({'key':i,'value':'v_%d'%i})



    if request.method == 'POST':
        logging.info(request.POST)


    val = request.session['counter']
    if val is None:
        val = 0
    request.session['counter']=val+1

    if val > 3:
        request.session.clear()


    
    return render_to_response('admin/test.html', RequestContext(request, { 'now': now, 'localized_now': localized_now, 'local_now': local_now, 'local_s': local_s, 'lines':lines }))

