
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

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'apps.teams.moderation_views',

    url('^team/(?P<team_id>\d+)/$', 'edit_moderation', name='edit_moderation'),                                         
    url(r'team/(?P<team_id>\d+)/videos/$', 'get_pending_videos', name='get-pending-videos'),
    url(r'team/(?P<team_id>\d+)/revisions/(?P<version_id>\d+)/remove-approval/$', 'remove_moderation_version', name='revision-remove-approval'),
    
    url(r'team/(?P<team_id>\d+)/revision/(?P<version_id>\d+)/approve/', 'approve_version', name='revision-approve'),
    url(r'team/(?P<team_id>\d+)/revisions/approves/$', 'batch_approve_version', name='revision-approve-batch'),
    url(r'team/(?P<team_id>\d+)/lang/(?P<lang_id>\d+)/revisions/approve-before/(?P<before_rev>\d+)/$', 'batch_approve_version', name='revision-approve-batch-until'),
    url(r'team/(?P<team_id>\d+)/revision/(?P<version_id>\d+)/reject/$', 'reject_version', name='revision-reject'),
    url(r'team/(?P<team_id>\d+)//lang/(?P<lang_id>\d+)/revisions/reject-before/(?P<before_rev>\d+)/$', 'batch_reject_version', name='revision-reject-batch-until'),
    url(r'team/(?P<team_id>\d+)/revision/(?P<version_id>\d+)/remove-moderation/$', 'remove_moderation_version', name='revision-remove-moderation'),
    url(r'team/(?P<team_id>\d+)/affect-selected/$', 'affect_selected', name='affect-selected'),
    url(r'team/(?P<team_id>\d+)/approve-all-for-video/(?P<video_id>\w+)/before/(?P<timestamp>\d+)/$', 'approve_all_for_video', name='approve-all-for-video'),
)
