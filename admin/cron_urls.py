from django.conf.urls.defaults import *
urlpatterns = patterns('admin',
    (r'^clean_expired_enrolls/$', 'cron_jobs.clean_expired_enrolls'),
)
