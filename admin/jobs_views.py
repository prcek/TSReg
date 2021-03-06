

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
from admin.models import Job

import logging
import datetime


def index(request):
    now = datetime.datetime.utcnow()

    jobs = Job.list_active()
    e_jobs = Job.list_error()

    return render_to_response('admin/jobs_index.html', RequestContext(request, { 'now': now, 'jobs':jobs, 'e_jobs':e_jobs }))


def wait(request,job_id):
    now = datetime.datetime.utcnow()
    job = Job.get_by_id(int(job_id))

    if job is None:
        raise Http404

    if not job.active:
        return HttpResponseRedirect(job.finish_target)

    return render_to_response('admin/jobs_wait.html', RequestContext(request, { 'now': now, 'job':job }))

def delete(request,job_id):
    job = Job.get_by_id(int(job_id))

    if job is None:
        raise Http404


    job.active=False
    job.save()


    return HttpResponseRedirect('../..')





