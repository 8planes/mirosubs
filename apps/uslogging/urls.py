from django.conf.urls.defaults import *

urlpatterns = patterns(
    'uslogging.views',
    url('^widget_logs/$', 'widget_logs', name='widget_logs'),
    url('^widget_log/(?P<log_pk>\d+)/$', 'widget_log', name='widget_log'),)
