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

urlpatterns = patterns('videos.views',
    url(r'^$', 'video_list', name='list'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^create/$', 'create', name='create'),    
    url(r'^email_friend/$', 'email_friend', name='email_friend'),
    url(r'^demo/$', 'demo', name='demo'),
    url(r'^activities/$', 'actions_list', name='actions_list'),
    url(r'^history/(?P<video_id>(\w|-)+)/$', 'history', name='history'),
    url(r'^history/(?P<video_id>(\w|-)+)/(?P<lang>\w+)/$', 'translation_history', name='translation_history'),
    url(r'^test/$', 'test_form_page', name='test_form_page'),
    url(r'(?P<video_id>(\w|-)+)/$', 'video', name='video'),
)