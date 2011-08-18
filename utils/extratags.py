from django import template
from django.utils import html
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

