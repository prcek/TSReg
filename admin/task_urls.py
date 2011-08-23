from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^send_check_email/$', 'tasks.send_check_email'),
    (r'^send_confirm_email/$', 'tasks.send_confirm_email'),
)
