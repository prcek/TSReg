from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^clean_expired_enrolls/$', 'cron_jobs.clean_expired_enrolls'),
    (r'^check_for_course_backup/$', 'cron_jobs.check_for_course_backup'),
    (r'^plan_course_backup/$', 'cron_jobs.plan_course_backup'),
    (r'^udpate_folder_stats/$', 'cron_jobs.udpate_folder_stats'),
)
