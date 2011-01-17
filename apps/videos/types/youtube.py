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
from gdata.service import RequestError
import re
import urllib
from utils import YoutubeSubtitleParser
from base import VideoType, VideoTypeError
from auth.models import CustomUser as User
from datetime import datetime
import random
from django.utils.translation import ugettext_lazy as _, ugettext

yt_service = YouTubeService()
yt_service.ssl = False

_('Private video')
_('Undefined error')

class YoutubeVideoType(VideoType):
    
    _url_pattern = re.compile(
        r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)')

    abbreviation = 'Y'
    name = 'Youtube' 
    site = 'youtube.com'
    
    def __init__(self, url):
        self.url = url
        self.videoid = self._get_video_id(self.url)
        self.entry = self._get_entry(self.video_id)

    @property
    def video_id(self):
        return self.videoid
    
    def convert_to_video_url(self):
        return 'http://www.youtube.com/watch?v=%s' % self.video_id   

    @classmethod    
    def video_url(cls, obj):
        if obj.videoid:
            return 'http://www.youtube.com/watch?v=%s' % obj.videoid
        else:
            return obj.url
    
    @classmethod
    def matches_video_url(cls, url):
        return 'youtube.com' in url and cls._get_video_id(url)

    def create_kwars(self):
        return {'videoid': self.video_id}

    def set_values(self, video_obj):
        video_obj.youtube_videoid = self.video_id
        video_obj.title = self.entry.media.title.text or ''
        if self.entry.media.description:
            video_obj.description = self.entry.media.description.text or ''
        if self.entry.media.duration:
            video_obj.duration = int(self.entry.media.duration.seconds)
        if self.entry.media.thumbnail:
            video_obj.thumbnail = self.entry.media.thumbnail[-1].url
        video_obj.save()
        self._get_subtitles_from_youtube(video_obj)
        return video_obj
    
    def _get_entry(self, video_id):
        try:
            return yt_service.GetYouTubeVideoEntry(video_id=str(video_id))
        except RequestError, e:
            err = e[0].get('body', 'Undefined error')
            raise VideoTypeError('Youtube error: %s' % err)        
    
    @classmethod    
    def _get_video_id(cls, video_url):
        match = cls._url_pattern.search(video_url)
        return match and match.group('video_id')

    def _get_subtitles_from_youtube(self, video_obj):
        from videos.models import SubtitleLanguage, SubtitleVersion, Subtitle
        
        url = 'http://www.youtube.com/watch_ajax?action_get_caption_track_all&v=%s' % video_obj.youtube_videoid
        d = urllib.urlopen(url)
        parser = YoutubeSubtitleParser(d.read())

        if not parser:
            return
        
        language, create = SubtitleLanguage.objects.get_or_create(video=video_obj, language = parser.language)
        language.is_original = False
        language.is_forked = True
        language.save()
        
        try:
            version_no = language.subtitleversion_set.order_by('-version_no')[:1] \
                .get().version_no + 1
        except SubtitleVersion.DoesNotExist:
            version_no = 0
            
        version = SubtitleVersion(language=language)
        version.version_no = version_no
        version.datetime_started = datetime.now()
        version.user = User.get_youtube_anonymous()
        version.note = u'From youtube'
        version.is_forked = True
        version.save()

        for i, item in enumerate(parser):
            subtitle = Subtitle(**item)
            subtitle.version = version
            subtitle.subtitle_id = int(random.random()*10e12)
            subtitle.subtitle_order = i+1
            subtitle.save()
        version.finished = True
        version.save()

        language.was_complete = True
        language.is_complete = True
        language.save()
