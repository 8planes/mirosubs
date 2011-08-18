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

urlpatterns = patterns(
    'auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^create/$', 'create_user', name='create_user'),
    url(r'^delete/$', 'delete_user', name='delete_user'),
    url(r'^login_post/$', 'login_post', name='login_post'),
    url(r'^facebook_login/$', 'facebook_login', name='facebook_login'),
    url(r'^facebook_login_done/(?P<next>[^/]+)/$', 'facebook_login_done', name='facebook_login_done'),
    url(r'^twitter_login/$', 'twitter_login', name='twitter_login'),
    url(r'^twitter_login_done/$', 'twitter_login_done', name='twitter_login_done'),
    url(r'^user_list/$', 'user_list', name='user_list'),
)
