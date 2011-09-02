from django.conf.urls.defaults import *
urlpatterns = patterns('enroll.views',
    (r'^$', 'index'),
    (r'^kategorie/(?P<folder_id>\d+)/$','folder_index'),
    (r'^kurz/(?P<course_id>\d+)/$','attend'),
    (r'^prihlaska/(?P<ref_code>\w+)/$', 'show'),
    (r'^potvrdit/(?P<confirm_code>\w+)/$', 'confirm'),
)
