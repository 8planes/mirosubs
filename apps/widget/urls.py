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
from widget.srt_subs import TTMLSubtitles, TXTSubtitles, SRTSubtitles, SBVSubtitles

urlpatterns = patterns(
    'widget.views',
    url(r'^rpc/xd/(\w+)$', 'xd_rpc'),
    url(r'^null_rpc/xd/(\w+)$', 'xd_rpc', kwargs={'null':True}),
    url(r'^rpc/xhr/(\w+)$', 'rpc', name='rpc'),
    url(r'^null_rpc/xhr/(\w+)$', 'rpc', kwargs={'null':True}),
    url(r'^rpc/jsonp/(\w+)$', 'jsonp'),
    url(r'^null_rpc/jsonp/(\w+)$', 'jsonp', kwargs={'null':True}),
    url(r'^widgetize_demo/(\w+)$', 'widgetize_demo'),
    url(r'^statwidget_demo.html$', 'statwidget_demo'),
    url(r'^video_demo/(\w+)$', 'video_demo'),
    url(r'^download_srt/$', 'download_subtitles', 
        {'handler': SRTSubtitles}, name='download_srt'),
    url(r'^download_ssa/$', 'download_subtitles', name='download_ssa'),
    url(r'^download_ttml/$', 'download_subtitles', 
        {'handler': TTMLSubtitles}, name='download_ttml'),
    url(r'^download_txt/$', 'download_subtitles', 
        {'handler': TXTSubtitles}, name='download_txt'),
    url(r'^download_sbv/$', 'download_subtitles', 
        {'handler': SBVSubtitles}, name='download_sbv'),                  
    url(r'^download_null_srt/$', 'null_srt'),
    url(r'^save_emailed_translations/$', 
        'save_emailed_translations'),
)

urlpatterns += patterns(
    '',
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^twitter_login/', 'auth.views.twitter_login', 
        kwargs={'next': '/widget/close_window/'}),
    url(r'^facebook_login/', 'auth.views.facebook_login'),
    url(r'^close_window/$', 
        'django.views.generic.simple.direct_to_template', 
        {'template' : 'widget/close_window.html'}),
    url(r'^config.js$', 
        'django.views.generic.simple.direct_to_template', 
        {'template': 'widget/config.js',
         'mimetype': 'text/javascript' }),
    url(r'^statwidgetconfig.js$', 
        'django.views.generic.simple.direct_to_template', 
        {'template': 'widget/statwidgetconfig.js',
         'mimetype': 'text/javascript' }),    
    url(r'^extension_demo.html$',
        'django.views.generic.simple.direct_to_template',
        {'template':'widget/extension_demo.html'})
)
