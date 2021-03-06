from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^send_student_email/$', 'tasks.send_student_email'),
    (r'^send_enroll_form_to_admin/$', 'tasks.send_enroll_form_to_admin'),
    (r'^send_enroll_form_to_admin/(?P<test_id>\d+)/$', 'tasks.send_enroll_form_to_admin'),
    (r'^recount_capacity/$', 'tasks.recount_capacity'),
    (r'^course_backup/$', 'tasks.course_backup'),
    (r'^course_fullsync/$', 'tasks.course_fullsync'),
    (r'^send_backup/$', 'tasks.send_backup'),
    (r'^hide_course_students/$', 'tasks.hide_course_students'),
    (r'^transfer_students/$', 'tasks.transfer_students'),
    (r'^makecopy_students/$', 'tasks.makecopy_students'),
    (r'^prepare_cards/$', 'tasks.prepare_cards'),
    (r'^prepare_qcards/$', 'tasks.prepare_qcards'),
    (r'^prepare_cardout/$', 'tasks.prepare_cardout'),
    (r'^hide_students/$', 'tasks.hide_students'),
    (r'^prepare_invitations/$', 'tasks.prepare_invitations'),
    (r'^plan_multimail/$', 'tasks.plan_multimail'),
    (r'^send_mail/$', 'tasks.send_mail'),
    (r'^incoming_email/$', 'tasks.incoming_email'),
    (r'^update_folder_stats/$', 'tasks.update_folder_stats'),

    (r'^update_all_students/$', 'tasks.update_all_students'),
    (r'^update_all_students_for_season/$', 'tasks.update_all_students_for_season'),
    (r'^update_all_students_for_course/$', 'tasks.update_all_students_for_course'),
    (r'^update_all_students_do_one/$', 'tasks.update_all_students_do_one'),

    (r'^cdbsync_model/$', 'tasks.cdbsync_model')
)
