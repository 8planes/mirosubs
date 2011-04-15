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
from handlers import VideoHandler, SubtitleHandler, SubtitleLanguagesHandler
from piston.resource import Resource
from piston.doc import documentation_view
from api.authentication import ModelAuthentication
from api.resource import SubtitlesResource
from api import emitters

auth = ModelAuthentication()
ad = { 'authentication': auth }

video_handler = Resource(VideoHandler, **ad)
subtitles_languages_handler = Resource(SubtitleLanguagesHandler, **ad)
subtitle_handler = SubtitlesResource(SubtitleHandler, **ad)

urlpatterns = patterns('',
    url('^video/(?P<video_id>[\w-]+)/$', video_handler, name="video_handler"),
    url('^video/$', video_handler),
    url('^subtitles/languages/$', subtitles_languages_handler),
    url('^subtitles/$', subtitle_handler, name='subtitle_handler'),
    url('^documentation/$', documentation_view, name='documentation')
)