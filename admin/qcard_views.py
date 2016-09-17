# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
from google.appengine.ext import db

from admin.models import QCard
import utils.config as cfg
import utils.pdf as pdf
import utils.qrg as qrg
import logging
import urllib
import base64




def index(request):
    if (request.auth_info.admin):
        qcard_list=QCard.list_all()
    else:
        qcard_list=QCard.list_my(request.auth_info.email)

    return render_to_response('admin/qcards_index.html', RequestContext(request, { 'qcard_list': qcard_list }))
    


def delete(request, qcard_id):


    qcard = QCard.get_by_id(int(qcard_id))

    if qcard is None:
        raise Http404

    qcard.delete()

    return HttpResponseRedirect('../..')


def clear_all(request):
    qcard_keys=QCard.keys_my(request.auth_info.email)
    db.delete(qcard_keys)

    return HttpResponseRedirect('..')

def clear_all_all(request):
    if not request.auth_info.admin:
        raise Http404

    qcard_keys=QCard.keys_all()

    db.delete(qcard_keys)

    return HttpResponseRedirect('..')


def print_all(request):




    logging.info("fetch qcards")
    qcard_list=QCard.list_my(request.auth_info.email)
    logging.info("fetch done")
    if qrg.qrg_cfg_get_on():
        logging.info("qrg is on")
        li = []
        for qc in qcard_list:
            li += [db.to_dict(qc)]
        rd = qrg.qrg_post("cards",li)
        pdfdata = base64.b64decode(rd["data"]) 
        r =  HttpResponse(pdfdata, mimetype='application/pdf')
        file_name = urllib.quote("karty.pdf")
        logging.info(file_name)
        r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name

    else:
        logging.info("qrg is off")
        r =  HttpResponse(mimetype='application/pdf')
        file_name = urllib.quote("karty.pdf")
        logging.info(file_name)
        r['Content-Disposition'] = "attachment; filename*=UTF-8''%s"%file_name
        pdf.students_qcard(r,qcard_list)

    return r

