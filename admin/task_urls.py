from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^send_student_email/$', 'tasks.send_student_email'),
    (r'^recount_capacity/$', 'tasks.recount_capacity'),
    (r'^hide_course_students/$', 'tasks.hide_course_students'),
    (r'^transfer_students/$', 'tasks.transfer_students'),
    (r'^prepare_cards/$', 'tasks.prepare_cards'),
    (r'^prepare_invitations/$', 'tasks.prepare_invitations'),
)
