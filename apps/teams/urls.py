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
from teams.rpc import rpc_router

urlpatterns = patterns('teams.views',
    url('^$', 'index', name='index'),
    url('^my/$', 'index', {'my_teams': True}, name='user_teams'),
    url('^create/$', 'create', name='create'),
    url('^invite/$', 'invite', name='invite'),
    url(r'^router/$', rpc_router, name='rpc_router'),
    url(r'^router/api/$', rpc_router.api, name='rpc_api'),
    url('^invite/accept/(?P<invite_pk>\d+)/$', 'accept_invite', name='accept_invite'),
    url('^invite/deny/(?P<invite_pk>\d+)/$', 'accept_invite', {'accept': False}, name='deny_invite'),
    url('^edit/(?P<slug>[-\w]+)/$', 'edit', name='edit'),
    url('^complete/(?P<slug>[-\w]+)/$', 'completed_videos', name='completed_videos'),
    url('^join_team/(?P<slug>[-\w]+)/$', 'join_team', name='join_team'),
    url('^highlight/(?P<slug>[-\w]+)/$', 'highlight', name='highlight'),
    url('^unhighlight/(?P<slug>[-\w]+)/$', 'highlight', {'highlight': False}, name='unhighlight'),    
    url('^applications/(?P<slug>[-\w]+)/$', 'applications', name='applications'),
    url('^application/approve/(?P<slug>[-\w]+)/(?P<user_pk>\d+)/$', 'approve_application', name='approve_application'),
    url('^application/deny/(?P<slug>[-\w]+)/(?P<user_pk>\d+)/$', 'deny_application', name='deny_application'),
    url('^add/video/(?P<slug>[-\w]+)/$', 'add_video', name='add_video'),
    url('^edit/videos/(?P<slug>[-\w]+)/$', 'edit_videos', name='edit_videos'),
    url('^edit/video/(?P<team_video_pk>\d+)/$', 'team_video', name='team_video'),
    url('^edit/logo/(?P<slug>[-\w]+)/$', 'edit_logo', name='edit_logo'),
    url('^edit/members/(?P<slug>[-\w]+)/$', 'edit_members', name='edit_members'),
    url('^remove/video/(?P<team_video_pk>\d+)/$', 'remove_video', name='remove_video'),
    url('^remove/members/(?P<slug>[-\w]+)/(?P<user_pk>\d+)/$', 'remove_member', name='remove_member'),
    url('^promote/members/(?P<slug>[-\w]+)/(?P<user_pk>\d+)/$', 'promote_member', name='promote_member'),
    url('^(?P<slug>[-\w]+)/(?P<is_debugging>debug/)?$', 'detail', name='detail'),
    url('^(?P<slug>[-\w]+)/members/$', 'detail_members', name='detail_members'),
    url('^(?P<slug>[-\w]+)/videos_actions/$', 'videos_actions', name='videos_actions'),
)

urlpatterns += patterns('',
    ('^t1$', 'django.views.generic.simple.direct_to_template', {
        'template': 'jsdemo/teams_profile.html'
    }),
)

