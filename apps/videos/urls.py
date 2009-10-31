from django.conf.urls.defaults import *

urlpatterns = patterns('videos.views',
    url(r'^$', 'video_list', name='list'),
    url(r'^create/$', 'create', name='create'),
    url(r'(?P<video_id>(\w|-)+)/$', 'video', name='video'),
)