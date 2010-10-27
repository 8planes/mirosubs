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
import re
import urllib
from videos.utils import YoutubeSubtitleParser
from base import VideoType
from auth.models import CustomUser as User
from datetime import datetime
import random

yt_service = YouTubeService()
yt_service.ssl = False

class YoutubeVideoType(VideoType):

    _url_pattern = re.compile(
        r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)')

    def __init__(self):
        self.abbreviation = 'Y'
        self.name = 'Youtube'   
    
    def video_url(self, obj):
        return 'http://www.youtube.com/watch?v=%s' % obj.youtube_videoid

    def matches_video_url(self, url):
        return 'youtube.com' in url and self._get_video_id(url)

    def create_kwars(self, video_url):
        return {'youtube_videoid': self._get_video_id(video_url)}

    def set_values(self, video_obj, video_url):
        video_id = self._get_video_id(video_url)
        video_obj.youtube_videoid = video_id
        entry = yt_service.GetYouTubeVideoEntry(video_id=video_obj.youtube_videoid)
        video_obj.title = entry.media.title.text
        if entry.media.duration:
            video_obj.duration = entry.media.duration.seconds
        if entry.media.thumbnail:
            video_obj.thumbnail = entry.media.thumbnail[-1].url
        video_obj.save()
        self._get_subtitles_from_youtube(video_obj)
        return video_obj
        
    def _get_video_id(self, video_url):
        return self._url_pattern.search(video_url).group('video_id')

    def _get_subtitles_from_youtube(self, video_obj):
        from videos.models import SubtitleLanguage, SubtitleVersion, Subtitle
        
        url = 'http://www.youtube.com/watch_ajax?action_get_caption_track_all&v=%s' % video_obj.youtube_videoid
        d = urllib.urlopen(url)
        parser = YoutubeSubtitleParser(d.read())
        
        if not parser:
            return
        
        language = SubtitleLanguage(video=video_obj)
        language.is_original = False
        language.is_forked = True
        language.language = parser.language
        language.save()
        
        version = SubtitleVersion(language=language)
        version.datetime_started = datetime.now()
        version.user = User.get_youtube_anonymous()
        version.note = u'From youtube'
        version.save()
        
        for i, item in enumerate(parser):
            subtitle = Subtitle(**item)
            subtitle.version = version
            subtitle.subtitle_id = int(random.random()*10e12)
            subtitle.sub_order = i+1
            subtitle.save()
        
        version.finished = True
        version.save()
        
        language.was_complete = True
        language.is_complete = True
        language.save()