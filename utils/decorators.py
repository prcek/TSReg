from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden


import logging


def ar_edit(function):
    def wrapper(request, *args, **kw):
        logging.info('ar_edit required')
        if request.auth_info.edit:
            logging.info('ar_edit ok')
            return function(request, *args, **kw)
        return HttpResponseForbidden()
    return wrapper

