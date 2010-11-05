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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from django.conf.urls.defaults import *

urlpatterns = patterns('teams.views',
    url('^$', 'index', name='index'),
    url('^create/$', 'create', name='create'),
    url('^invite/$', 'invite', name='invite'),
    url('^invite/accept/(?P<pk>\d+)/$', 'accept_invite', name='accept_invite'),
    url('^invite/deny/(?P<pk>\d+)/$', 'accept_invite', {'accept': False}, name='deny_invite'),
    url('^edit/(?P<pk>\d+)/$', 'edit', name='edit'),
    url('^highlight/(?P<pk>\d+)/$', 'highlight', name='highlight'),
    url('^unhighlight/(?P<pk>\d+)/$', 'highlight', {'highlight': False}, name='unhighlight'),    
    url('^applications/(?P<pk>\d+)/$', 'applications', name='applications'),
    url('^application/approve/(?P<pk>\d+)/(?P<user_pk>\d+)/$', 'approve_application', name='approve_application'),
    url('^application/deny/(?P<pk>\d+)/(?P<user_pk>\d+)/$', 'deny_application', name='deny_application'),
    url('^add/video/(?P<pk>\d+)/$', 'add_video', name='add_video'),
    url('^edit/videos/(?P<pk>\d+)/$', 'edit_videos', name='edit_videos'),
    url('^edit/video/(?P<pk>\d+)/$', 'team_video', name='team_video'),
    url('^edit/members/(?P<pk>\d+)/$', 'edit_members', name='edit_members'),
    url('^remove/video/(?P<pk>\d+)/$', 'remove_video', name='remove_video'),
    url('^remove/members/(?P<pk>\d+)/(?P<user_pk>\d+)/$', 'remove_member', name='remove_member'),
    url('^demote/members/(?P<pk>\d+)/(?P<user_pk>\d+)/$', 'demote_member', name='demote_member'),
    url('^promote/members/(?P<pk>\d+)/(?P<user_pk>\d+)/$', 'promote_member', name='promote_member'),
    url('^(?P<pk>\d+)/$', 'detail', name='detail'),
    url('^(?P<pk>\d+)/members/$', 'detail_members', name='detail_members'),
    url('^(?P<pk>\d+)/videos_actions/$', 'videos_actions', name='videos_actions'),
    url('^(?P<pk>\d+)/members_actions/$', 'members_actions', name='members_actions'),
)

urlpatterns += patterns('',
    ('^t1$', 'django.views.generic.simple.direct_to_template', {
        'template': 'jsdemo/teams_profile.html'
    }),
)