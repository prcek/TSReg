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

    folder_stats = []
    if not season is None:
    	folder_stats = FolderStats.list_by_season(str(season.key()))



    ts_em = 0
    ts_ef = 0
    ts_e = 0

    ts_pm = 0
    ts_pf = 0
    ts_p = 0

    ts_ppm = 0 
    ts_ppf = 0
    ts_pp = 0

    ts_npm = 0
    ts_npf = 0
    ts_np = 0

    ts_sum = 0

    for fs in folder_stats:
        ts_em = ts_em + fs.stat_em
        ts_ef = ts_ef + fs.stat_ef
        ts_e = ts_e + fs.stat_e

        ts_pm = ts_pm + fs.stat_pm
        ts_pf = ts_pf + fs.stat_pf
        ts_p = ts_p + fs.stat_p

        ts_ppm = ts_ppm + fs.stat_ppm
        ts_ppf = ts_ppf + fs.stat_ppf
        ts_pp = ts_pp + fs.stat_pp
 
        ts_npm = ts_npm + fs.stat_npm
        ts_npf = ts_npf + fs.stat_npf
        ts_np = ts_np + fs.stat_np

        ts_sum = ts_sum + fs.stat_sum

    return render_to_response('admin/index.html', RequestContext(request, {
    	'form': form, 'folder_stats':folder_stats, 
        'ts_em': ts_em, 'ts_ef': ts_ef, 'ts_e': ts_e,
        'ts_pm': ts_pm, 'ts_pf': ts_pf, 'ts_p': ts_p,
        'ts_ppm': ts_ppm, 'ts_ppf': ts_ppf, 'ts_pp': ts_pp,
        'ts_npm': ts_npm, 'ts_npf': ts_npf, 'ts_np': ts_np,
        'ts_sum':ts_sum
    	}))

