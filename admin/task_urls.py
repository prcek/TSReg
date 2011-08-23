from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^send_check_email/$', 'tasks.send_check_email'),
    (r'^send_confirm_email/$', 'tasks.send_confirm_email'),
    (r'^send_enroll_yes_email/$', 'tasks.send_enroll_yes_email'),
    (r'^send_enroll_no_email/$', 'tasks.send_enroll_no_email'),
    (r'^recount_capacity/$', 'tasks.recount_capacity'),
)
