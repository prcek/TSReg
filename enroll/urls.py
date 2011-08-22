from django.conf.urls.defaults import *
urlpatterns = patterns('enroll.views',
    (r'^$', 'index'),
    (r'^kurz/(?P<course_id>\d+)/$','attend'),
    (r'^prihlaska/(?P<ref_code>\w+)/$', 'show'),
)
