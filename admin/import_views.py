# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging
import datetime
from utils.locale import local_timezone

ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}


ACTION_CHOICES = (
    ('-','--- zvol akci ---'),
    ('import_students','import žáků'),
)



class UploadFileForm(forms.Form):
    action = forms.CharField(label='akce', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=ACTION_CHOICES))
#    post_action_ok = forms.CharField(widget=forms.widgets.HiddenInput())
#    post_action_error = forms.CharField(widget=forms.widgets.HiddenInput())
    file = forms.FileField(label='soubor')


def index(request):

    if request.method == 'POST':
        logging.info(request.POST)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logging.info('file upload - "%s"' % request.FILES['file'])
#            return redirect('/utils/files/')
    else:
        form = UploadFileForm()


    return render_to_response('admin/import_index.html', RequestContext(request, {  'form': form}))

