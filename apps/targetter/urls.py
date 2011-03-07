from django.conf.urls.defaults import *

urlpatterns = patterns('targetter.views',
    url('^load/$', 'load', name='load'),
    url('^test/(?P<pk>\d+)/$', 'test', name='test'),
)