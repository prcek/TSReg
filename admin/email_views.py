# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader
import utils.config as cfg
import utils.mail as mail
from admin.models import EMailList
import re
import logging


ERROR_MESSAGES={'required': 'Položka musí být vyplněna', 'invalid': 'Neplatná hodnota'}

class EMailListField(forms.CharField):
    def clean(self, value):
        value = re.sub(r'[,;]'," ",value)
        s = set([])
        for e in value.split():
            if  re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e) != None:
                s.add(e)
        return u'\n'.join(sorted(s))


class EMailListWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        l = value.split()  
        gl = mail.chunks(l,5)
        lines = []
        for g in gl:
            lines.append(u', '.join(g))
        value = u'\n'.join(lines)
        return super(EMailListWidget,self).render(name,value,attrs)

class EMailListChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        self._set_choices(EMailList.get_EMAILLIST_CHOICES())
        return super(EMailListChoiceField,self).valid_value(value)


class EMailListForm(forms.ModelForm):
    name = forms.CharField()
    desc = forms.CharField(required=False)
    emails = EMailListField(widget=EMailListWidget(attrs={'cols':160, 'rows':20}), required=False, label="emaily")
    class Meta:
        model = EMailList 
        fields = ( 'name','desc', 'emails' )

def index(request):
    els = EMailList.list_all()
    return render_to_response('admin/email_index.html', RequestContext(request, { 'list': els  }))

class EmailShowForm(forms.Form):
    gsize = forms.IntegerField(label='skupinky po', error_messages=ERROR_MESSAGES,  required=False, initial=40)
 
def show(request, el_id):
    el = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404

    gsize = 40
    if request.method == 'POST':
        form = EmailShowForm(request.POST)
        if form.is_valid():
            gsize = form.cleaned_data['gsize']
        else:
            gsize = None
    else: 
        form = EmailShowForm()


    if gsize:
        emails = el.emails
        emails = sorted(list(set(emails)))
        ecount = len(emails)            
          
        if gsize>0: 
            groups = mail.chunks(emails,gsize) 
        else:
            groups = [emails]
    else: 
        emails=None
        groups=None
        ecount=None
        

    return render_to_response('admin/email_show.html', RequestContext(request, { 'form':form, 'el': el, 
        'list': emails,  
        'groups': groups,
        'count': ecount,
 }))

def create(request):
    if request.method == 'POST':
        form = EMailListForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            el  = form.save(commit=False)
            el.save()
            logging.info('new el created - %s' % (el))
            return redirect('..')
    else:
        form = EMailListForm() 
    return render_to_response('admin/email_create.html', RequestContext(request, { 'form': form }))

def edit(request, el_id):
    el = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404
    if request.method == 'POST':
        form = EMailListForm(request.POST, instance=el)
        if form.is_valid():
            logging.info('edit el before - %s' % (el))
            form.save(commit=False)
            logging.info('edit el after - %s' % (el))
            el.save()
            return redirect('../..')
    else:
        form = EMailListForm(instance=el)
    return render_to_response('admin/email_edit.html', RequestContext(request, { 'form': form }) ) 


def delete(request, el_id):

    el  = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404

    el.delete()
    return redirect('../..')


EA_CHOICES=(
    ('email_nop','----- zvol operaci -----'),
    ('email_add','do aktuální přidat obsah druhé'),
    ('email_del','z aktuální odebrat obsah druhé'),
    ('email_assign','aktuální přepsat obsahem druhé'),
)

 
class EMailActionForm(forms.Form):
    action = forms.CharField(label='akce', error_messages=ERROR_MESSAGES, widget = forms.Select(choices=EA_CHOICES))
    list_key = EMailListChoiceField(label='druhá skupina', error_messages=ERROR_MESSAGES)
    def __init__(self,data = None, **kwargs):
        super(self.__class__,self).__init__(data, **kwargs)
        self.fields['list_key']._set_choices(EMailList.get_EMAILLIST_CHOICES())


 

def action(request, el_id):
    el  = EMailList.get_by_id(int(el_id))
    if el is None:
        raise Http404
    if request.method == 'POST':
        form = EMailActionForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = EMailActionForm()
 
    return render_to_response('admin/email_action.html', RequestContext(request, { 'el':el, 'form': form }) ) 

