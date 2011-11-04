from django import template
from django.utils import html
from utils.locale import local_timezone
register = template.Library()

@register.filter
def anone(v):
    if v is None:
        return "?"
    elif v:
        return 'Ano'
    else:
        return 'Ne'
    return None 

@register.filter
def nonone(v):
    if v is None:
        return ""
    return v

@register.filter
def localdatetime(v):
    if v is None:
        return None
    return local_timezone.fromutc(v)
    

@register.filter
def shortdatetime(v):
    if v is None:
        return None
    return local_timezone.fromutc(v).strftime("%d.%m.%Y %H:%M")

    
