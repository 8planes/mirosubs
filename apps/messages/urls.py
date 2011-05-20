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
from django.conf.urls.defaults import patterns, url
from messages.views import rpc_router

urlpatterns = patterns('messages.views',
    url('^$', 'index', name='index'),
    url('^(?P<message_pk>[\d]+)/$', 'message_detail', name='detail'),                   
    url('^sent/$', 'sent', name='sent'), 
    url(r'^router/$', rpc_router, name='rpc_router'),
    url(r'^router/api/$', rpc_router.api, name='rpc_api'),    
)
