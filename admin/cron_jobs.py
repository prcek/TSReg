# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from enroll.models import Student,Course
import utils.config as cfg


import logging

def clean_expired_enrolls(request):

    return HttpResponse('ok')
