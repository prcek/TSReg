from django.conf.urls.defaults import *
urlpatterns = patterns('enroll.views',
    (r'^$', 'index'),
#    (r'^kategorie/(?P<folder_id>\d+)/$','folder_index'),
    (r'^kurz/(?P<course_id>\d+)/$','attend'),
    (r'^kurz/(?P<course_id>\d+)/s/$','attend_force_single'),
    (r'^prihlaska/(?P<ref_code>\w+)/$', 'show'),
    (r'^prihlasky/(?P<ref_code1>\w+)/(?P<ref_code2>\w+)/$', 'show_pair'),
    (r'^potvrdit/(?P<confirm_code>\w+)/$', 'confirm'),
    (r'^potvrdit/(?P<confirm_code1>\w+)/(?P<confirm_code2>\w+)/$', 'confirm_pair'),
)
