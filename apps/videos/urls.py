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
from models import TranslationVersion

urlpatterns = patterns('videos.views',
    url(r'^$', 'video_list', name='list'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^upload_subtitles/$', 'upload_subtitles', name='upload_subtitles'),
    url(r'^create/$', 'create', name='create'),    
    url(r'^email_friend/$', 'email_friend', name='email_friend'),
    url(r'^demo/$', 'demo', name='demo'),
    url(r'^activities/$', 'actions_list', name='actions_list'),
    url(r'^change_video_title', 'ajax_change_video_title', name='ajax_change_video_title'),
    url(r'^stop_notification/(?P<video_id>(\w|-)+)/$', 'stop_notification', name='stop_notification'),    
    url(r'^revision/last/(?P<video_id>(\w|-)+)/$', 'last_revision', name='last_revision'),
    url(r'^revision/last/(?P<video_id>(\w|-)+)/(?P<language_code>[\w\-]+)/$', 'last_translation_revision', name='last_translation_revision'),
    url(r'^revision/(?P<pk>\d+)/$', 'revision', name='revision'),
    url(r'^revision/t(?P<pk>\d+)/$', 'revision', {'cls': TranslationVersion}, 'translation_revision'),
    url(r'^rollback/(?P<pk>\d+)/$', 'rollback', name='rollback'),
    url(r'^rollback/t(?P<pk>\d+)/$', 'rollback', {'cls': TranslationVersion}, 'translation_rollback'),
    url(r'^diffing/(?P<first_pk>\d+)/(?P<second_pk>\d+)/$', 'diffing', name='diffing'),
    url(r'^diffing/t(?P<first_pk>\d+)/t(?P<second_pk>\d+)/$', 'translation_diffing', name='translation_diffing'),
    url(r'^test/$', 'test_form_page', name='test_form_page'),
    url(r'^(?P<video_id>(\w|-)+)/original/$', 'history', name='history'),
    url(r'^(?P<video_id>(\w|-)+)/(?P<lang>[\w\-]+)/$', 'history', name='translation_history'),
    url(r'(?P<video_id>(\w|-)+)/$', 'video', name='video'),
)
