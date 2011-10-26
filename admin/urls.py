from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^$', 'views.index'),
    (r'^sys/$', 'sys_views.index'),
    (r'^sys/add/$', 'sys_views.config_create'),
    (r'^sys/(?P<config_id>\d+)/', 'sys_views.config_edit'),
    (r'^sys/setup/$', 'sys_views.config_setup'),
    (r'^sys/test/$', 'test_views.index'),
    (r'^sys/jobs/$', 'jobs_views.index'),
    (r'^sys/jobs/(?P<job_id>\d+)/del/$', 'jobs_views.delete'),


    (r'^kurzy/$', 'course_views.index'),
    (r'^kurzy/add/$', 'course_views.create'),
    (r'^kurzy/(?P<course_id>\d+)/edit/$', 'course_views.edit'),
    (r'^kurzy/(?P<course_id>\d+)/del/$', 'course_views.delete'),
    (r'^kurzy/(?P<course_id>\d+)/recount/$', 'course_views.recount'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/$', 'student_views.index_course'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/edit/$', 'student_views.edit'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/enroll/$', 'student_views.enroll'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/kick/$', 'student_views.kick'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/spare/$', 'student_views.spare'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/view/$', 'student_views.view'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/(?P<student_id>\d+)/email/$', 'student_views.email'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/add/$', 'student_views.create'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/add_pair/$', 'student_views.create_pair'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/email/$', 'student_views.course_emails'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/csv/$', 'student_views.course_as_csv'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/pdf_list/$', 'student_views.course_as_pdf'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/pdf_enroll/$', 'student_views.enroll_as_pdf'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/op/$', 'student_views.action_course'),
    (r'^kurzy/\d+/zaci/wait/(?P<job_id>\d+)/$', 'jobs_views.wait'),

    (r'^karty/$', 'card_views.index'),
    (r'^karty/add/$', 'card_views.create'),
    (r'^karty/(?P<card_id>\d+)/edit/$', 'card_views.edit'),
    (r'^karty/(?P<card_id>\d+)/del/$', 'card_views.delete'),
    (r'^karty/clear/$', 'card_views.clear_all'),
    (r'^karty/clear_all/$', 'card_views.clear_all_all'),
    (r'^karty/print/$', 'card_views.print_all'),

    (r'^adresy/$', 'invitation_views.index'),
    (r'^adresy/add/$', 'invitation_views.create'),
    (r'^adresy/(?P<invitation_id>\d+)/edit/$', 'invitation_views.edit'),
    (r'^adresy/(?P<invitation_id>\d+)/del/$', 'invitation_views.delete'),
    (r'^adresy/clear/$', 'invitation_views.clear_all'),
    (r'^adresy/clear_all/$', 'invitation_views.clear_all_all'),
    (r'^adresy/print/$', 'invitation_views.print_all'),

    (r'^inflect/$', 'inflect_views.index'),
    (r'^inflect/add/$', 'inflect_views.create'),
    (r'^inflect/test/$', 'inflect_views.test'),
    (r'^inflect/(?P<inflect_id>\d+)/edit/$', 'inflect_views.edit'),
    (r'^inflect/(?P<inflect_id>\d+)/del/$', 'inflect_views.delete'),
    (r'^inflect/clear_all/$', 'inflect_views.clear_all'),
    (r'^inflect/setup/$', 'inflect_views.setup'),


    (r'^kategorie/$', 'folder_views.index'),
    (r'^kategorie/add/$', 'folder_views.create'),
    (r'^kategorie/(?P<folder_id>\d+)/edit/$', 'folder_views.edit'),
    (r'^kategorie/(?P<folder_id>\d+)/del/$', 'folder_views.delete'),

    (r'^sezony/$', 'season_views.index'),
    (r'^sezony/add/$', 'season_views.create'),
    (r'^sezony/(?P<season_id>\d+)/edit/$', 'season_views.edit'),
    (r'^sezony/(?P<season_id>\d+)/del/$', 'season_views.delete'),
 

    (r'^zaci/$', 'student_views.index'),
    (r'^zaci/add/$', 'student_views.create'),
    (r'^zaci/(?P<student_id>\d+)/edit/$', 'student_views.edit'),
    (r'^zaci/(?P<student_id>\d+)/email/$', 'student_views.email'),

    
    (r'^nahled/zapis/$', 'preview_views.enroll'), 



    (r'^import/$', 'import_views.index'),
    (r'^import/(?P<file_id>\d+)/import_students/$', 'import_views.import_students'),
    (r'^import/(?P<file_id>\d+)/import_students/(?P<seq_id>\d+)/$', 'import_views.import_students'),
    (r'^import/(?P<file_id>\d+)/import_students/lines/(?P<start_line>\d+)/(?P<end_line>\d+)/to/(?P<course_id>\d+)/$', 'import_views.import_students_do'),
 

    (r'^backup/$', 'backup_views.index'),
    (r'^backup/(?P<course_id>\d+)/do/$', 'backup_views.plan_backup'),
    (r'^backup/(?P<course_id>\d+)/$', 'backup_views.index_course'),
    (r'^backup/(?P<course_id>\d+)/(?P<course_backup_id>\d+)/$', 'backup_views.get_backup'),

    (r'^opt/$', 'opt_views.index'),
    (r'^help/$', 'help_views.index'),
)
