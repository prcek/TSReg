from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^$', 'views.index'),
    (r'^sys/$', 'sys_views.index'),
    (r'^sys/add/$', 'sys_views.config_create'),
    (r'^sys/(?P<config_id>\d+)/', 'sys_views.config_edit'),
    (r'^sys/setup/$', 'sys_views.config_setup'),
    (r'^sys/test/$', 'test_views.index'),
    (r'^sys/jobs/$', 'jobs_views.index'),


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
    (r'^kurzy/(?P<course_id>\d+)/zaci/email/$', 'student_views.course_emails'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/csv/$', 'student_views.course_as_csv'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/pdf/$', 'student_views.course_as_pdf'),
    (r'^kurzy/(?P<course_id>\d+)/zaci/op/$', 'student_views.action_course'),
    (r'^kurzy/\d+/zaci/wait/(?P<job_id>\d+)/$', 'jobs_views.wait'),


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

    (r'^opt/$', 'opt_views.index'),
)
