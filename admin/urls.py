from django.conf.urls.defaults import *
urlpatterns = patterns('admin.views',
    (r'^$', 'index'),
    (r'^sys/$', 'sys_index'),
    (r'^sys/add/$', 'sys_config_create'),
    (r'^sys/(?P<config_id>\d+)/', 'sys_config_edit'),
    (r'^sys/setup/$', 'sys_setup'),
    (r'^opt/$', 'opt_index'),
)
