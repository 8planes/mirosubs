from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'targetter/index.html'}, 'index'),
)

urlpatterns += patterns('targetter.views',
    url('^load/$', 'load', name='load'),
    url('^test/(?P<pk>\d+)/$', 'test', name='test'),
)