from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^create/$', 'videos.views.create', name='create'),
    url(r'(?P<video_id>(\w|-)+)/$', 'videos.views.video', name='video'),

)