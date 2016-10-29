from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden


import logging


def ar_card(function):
    def wrapper(request, *args, **kw):
        logging.info('ar_card required')
        if request.auth_info.card:
            logging.info('ar_card ok')
            return function(request, *args, **kw)
        return HttpResponseForbidden()
    return wrapper


def ar_edit(function):
    def wrapper(request, *args, **kw):
        logging.info('ar_edit required')
        if request.auth_info.edit:
            logging.info('ar_edit ok')
            return function(request, *args, **kw)
        return HttpResponseForbidden()
    return wrapper

def ar_power(function):
    def wrapper(request, *args, **kw):
        logging.info('ar_power required')
        if request.auth_info.power:
            logging.info('ar_power ok')
            return function(request, *args, **kw)
        return HttpResponseForbidden()
    return wrapper
