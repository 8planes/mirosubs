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
from widget.srt_subs import TTMLSubtitles, TXTSubtitles

urlpatterns = patterns(
    'widget.views',
    url(r'^rpc/xd/(\w+)$', 'xd_rpc'),
    url(r'^rpc/null_xd/(\w+)$', 'xd_rpc', kwargs={'null':True}),
    url(r'^rpc/xhr/(\w+)$', 'rpc'),
    url(r'^rpc/null_xhr/(\w+)$', 'rpc', kwargs={'null':True}),
    url(r'^rpc/jsonp/(\w+)$', 'jsonp'),
    url(r'^rpc/null_jsonp/(\w+)$', 'jsonp', kwargs={'null':True}),
    url(r'^download_srt/$', 'srt', name='download_srt'),
    url(r'^download_ssa/$', 'download_subtitles', name='download_ssa'),
    url(r'^download_ttml/$', 'download_subtitles', 
        {'handler': TTMLSubtitles}, name='download_ttml'),
    url(r'^download_txt/$', 'download_subtitles', 
        {'handler': TXTSubtitles}, name='download_txt'),        
    url(r'^download_null_srt/$', 'null_srt'),
)

urlpatterns += patterns(
    '',
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^twitter_login/', 'auth.views.twitter_login', 
        kwargs={'next': '/widget/close_window/'}),
    url(r'^close_window/$', 
        'django.views.generic.simple.direct_to_template', 
        {'template' : 'widget/close_window.html'}),
)
