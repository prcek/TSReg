from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^$', 'views.index'),
    (r'^sys/$', 'sys_views.index'),
    (r'^sys/add/$', 'sys_views.config_create'),
    (r'^sys/(?P<config_id>\d+)/', 'sys_views.config_edit'),
    (r'^sys/setup/$', 'sys_views.config_setup'),

    (r'^kurzy/$', 'course_views.index'),
    (r'^kurzy/add/$', 'course_views.create'),
    (r'^kurzy/(?P<course_id>\d+)/edit/$', 'course_views.edit'),


    (r'^zaci/$', 'student_views.index'),
    (r'^zaci/add/$', 'student_views.create'),
    (r'^zaci/(?P<student_id>\d+)/edit/$', 'student_views.edit'),


    (r'^opt/$', 'opt_views.index'),
)
