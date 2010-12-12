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

urlpatterns = patterns('profiles.views',
    url(r'^mine/$', 'my_profile', name='my_profile'),
    url(r'^edit/$', 'edit_profile', name='edit'),
    url(r'^send_message/$', 'send_message', name='send_message'),
    url(r'^edit_avatar/$', 'edit_avatar', name='edit_avatar'),
    url(r'^remove_avatar/$', 'remove_avatar', name='remove_avatar'),
    url(r'^(?P<user_id>.+)/$', 'profile', name='profile'),
)
