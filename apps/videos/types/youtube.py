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

from gdata.youtube.service import YouTubeService
from videos.types.base import registrar, VideoType
import re

yt_service = YouTubeService()
yt_service.ssl = False

class YoutubeVideoType(VideoType):
    abbreviation = "Y"
    name = "Youtube"
    _url_pattern = re.compile(
        r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)')

    def video_url(self, video_url_model):
        return 'http://www.youtube.com/watch?v={0}'.format(
            video_url_model.youtube_videoid)

    def matches_video_url(self, parsed_url):
        return 'youtube.com' in parsed_url.netloc

    def set_values(self, video_model, video_url):
        video_id = self._get_video_id(video_url)
        entry = yt_service.GetYouTubeVideoEntry(video_id=video_model.youtube_videoid)
        video_model.title = entry.media.title.text
        video_model.duration = entry.media.duration.seconds
        if entry.media.thumbnail:
            video_model.thumbnail = entry.media.thumbnail[-1].url

    def _get_video_id(self, video_url):
        return self._url_pattern.search(video_url).group('video_id')

    def _video_url_kwargs(self, video_url):
        return { 'youtube_videoid': self._get_video_id(video_url) }

registrar.register(YoutubeVideoType)
