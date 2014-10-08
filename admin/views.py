# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg

import logging

from enroll.models import Course,Folder,Season,FolderStats
from admin.course_views import SeasonFilterForm

def index(request):


    season = None
    if request.method == 'POST':
        form = SeasonFilterForm(request.POST)
        if form.is_valid():
            season = Season.get(str(form.cleaned_data['season_key']))
            if not season is None:
                request.session['course_season_key']=str(season.key())
    else:
        cskey = request.session.get('course_season_key',None)
        if not cskey is None:
            season =  Season.get(str(cskey))

        if (season is None):
            form = SeasonFilterForm()
        else:
            form = SeasonFilterForm({'season_key':str(season.key())})

    folder_stats = None
    if not season is None:
    	folder_stats = FolderStats.list_by_season(str(season.key()))

    total_sum = 0
    for fs in folder_stats:
         total_sum = total_sum + fs.stat_sum

    return render_to_response('admin/index.html', RequestContext(request, {
    	'form': form, 'folder_stats':folder_stats, 'total_sum':total_sum
    	}))

