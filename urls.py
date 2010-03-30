# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.sites.models import Site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', 
     {'template': 'index.html'}),
    url(r'^login/', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', name='logout', 
        kwargs={'next_page': '/'}),
    (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/password_reset/$', 
        'django.contrib.auth.views.password_reset', 
        name='password_reset'),
    (r'^password_reset/done/$', 
     'django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
     'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    (r'socialauth/', include('socialauth.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^embed_widget.js$', 'widget.views.embed'),
    url(r'^widget/twitter_login/', 'socialauth.views.twitter_login', 
        kwargs={'next': '/widget/close_window/'}),
    (r'^widget/rpc/xd/(\w+)$', 'widget.views.xd_rpc'),
    (r'^widget/rpc/xhr/(\w+)$', 'widget.views.rpc'),
    (r'^widget/login/$', 'django.contrib.auth.views.login'),
    (r'^widget/close_window/$', 
     'django.views.generic.simple.direct_to_template', 
     {'template' : 'widget/close_window.html'}),
    (r'^widget/download_srt/$', 'widget.views.srt'),
    (r'^widget/download_null_srt/$', 'widget.views.null_srt'),
    (r'^jstest/(\w+)', 'jstesting.views.jstest'),
    (r'^jsdemo/(\w+)', 'jsdemo.views.jsdemo'),
    (r'^videos/', include('videos.urls', namespace='videos', 
                          app_name='videos')),
    (r'^profiles/', include('profiles.urls', namespace='profiles', 
                            app_name='profiles')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'raw_template/(?P<template>.*)', 'django.views.generic.simple.direct_to_template'),
    )
