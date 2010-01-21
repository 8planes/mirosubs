from django.conf.urls.defaults import *

urlpatterns = patterns('profiles.views',
    url(r'^mine/$', 'my_profile', name='my_profile'),
    url(r'^(?P<user_id>.+)/$', 'profile', name='profile'),
)