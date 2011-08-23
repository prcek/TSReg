# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
import utils.config as cfg

import logging

def send_check_email(request):
    return HttpResponse('ok')
