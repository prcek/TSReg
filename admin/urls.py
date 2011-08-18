from django.conf.urls.defaults import *
urlpatterns = patterns('admin.views',
    (r'^$', 'index'),
    (r'^sys/$', 'sys_index'),
)
