
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
from videos.views import rpc_router

urlpatterns = patterns(
    'videos.views',
    url(r'^$', 'video_list', name='list'),
    url(r'^watch/$', 'watch_page', name='watch_page'),
    url(r'^watch/featured/$', 'featured_videos', name='featured_videos'),
    url(r'^watch/latest/$', 'latest_videos', name='latest_videos'),
    url(r'^watch/popular/$', 'popular_videos', name='popular_videos'),    
    url(r'^volunteer/$', 'volunteer_page', name='volunteer_page'),
    url(r'^volunteer/(?P<category>\w+)/$', 'volunteer_category', name='volunteer_category'),
    url(r'^test_celery/$', 'test_celery'),
    url(r'^test_celery_exception/$', 'test_celery_exception'),
    url(r'^router/$', rpc_router, name='rpc_router'),
    url(r'^router/api/$', rpc_router.api, name='rpc_api'),    
    url(r'^subscribe_to_updates/$', 'subscribe_to_updates', name='subscribe_to_updates'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^feedback/error/$', 'feedback', {'hide_captcha': True}, 'feedback_error'),
    url(r'^upload_subtitles/$', 'upload_subtitles', name='upload_subtitles'),
    url(r'^paste_transcription/$', 'paste_transcription', name='paste_transcription'),    
    url(r'^upload_transcription_file/$', 'upload_transcription_file', name='upload_transcription_file'),
    url(r'^create/$', 'create', name='create'),
    url(r'^create/feed/$', 'create_from_feed', name='create_from_feed'),
    url(r'^site_feedback/$', 'site_feedback', name='site_feedback'),
    url(r'^email_friend/$', 'email_friend', name='email_friend'),
    url(r'^demo/$', 'demo', name='demo'),
    url(r'^activities/(?P<video_id>(\w|-)+)/$', 'actions_list', name='actions_list'),
    url(r'^stop_notification/(?P<video_id>(\w|-)+)/$', 'stop_notification', name='stop_notification'),    
    url(r'^revision/(?P<pk>\d+)/$', 'revision', name='revision'),
    url(r'^rollback/(?P<pk>\d+)/$', 'rollback', name='rollback'),
    url(r'^diffing/(?P<first_pk>\d+)/(?P<second_pk>\d+)/$', 'diffing', name='diffing'),
    url(r'^test/$', 'test_form_page', name='test_form_page'),
    url(r'^video_url_make_primary/$', 'video_url_make_primary', name='video_url_make_primary'),
    url(r'^video_url_create/$', 'video_url_create', name='video_url_create'),
    url(r'^video_url_remove/$', 'video_url_remove', name='video_url_remove'),
    url(r'^(?P<video_id>(\w|-)+)/debug/$', 'video_debug', name='video_debug'),
    url(r'^(?P<video_id>(\w|-)+)/$', 'history', name='history'),
    url(r'(?P<video_id>(\w|-)+)/info/$', 'video', name='video'),
    url(r'(?P<video_id>(\w|-)+)/info/(?P<title>[^/]+)/$', 'video', name='video_with_title'),
    url(r'(?P<video_id>(\w|-)+)/url/(?P<video_url>\d+)/$', 'video', name='video_url'),
    url(r'^(?P<video_id>(\w|-)+)/(?P<lang>[\w\-]+)/(?P<lang_id>[\d]+)/$', 'history', name='translation_history'),
    url(r'^(?P<video_id>(\w|-)+)/(?P<lang>[\w\-]+)/$', 'legacy_history', name='translation_history_legacy'),
    url(r'(?P<video_id>(\w|-)+)/staff/delete/$', 'video_staff_delete', name='video_staff_delete'),
)
