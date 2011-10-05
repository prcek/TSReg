

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging
import datetime
from utils.locale import local_timezone

def index(request):

    if request.method == 'POST':
        logging.info(request.POST)

    return render_to_response('admin/import_index.html', RequestContext(request, {  }))

