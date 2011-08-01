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

from base import VideoType, VideoTypeError
import httplib
from django.utils import simplejson as json
import re
from django.utils.translation import ugettext_lazy as _

DAILYMOTION_REGEX = re.compile(r'https?://(?:[^/]+[.])?dailymotion.com/video/(?P<video_id>[-0-9a-zA-Z]+)(?:_.*)?')


class DailymotionVideoType(VideoType):

    abbreviation = 'D'
    name = 'dailymotion.com'   
    site = 'dailymotion.com'
    
    def __init__(self, url):
        self.url = url
        self.videoid = self.get_video_id(url)

    @property
    def video_id(self):
        return self.videoid
        
    def convert_to_video_url(self):
        return 'http://dailymotion.com/video/%s' % self.video_id

    @classmethod    
    def video_url(cls, obj):
        return 'http://dailymotion.com/video/%s' % obj.videoid
    
    @classmethod
    def matches_video_url(cls, url):
        video_id = cls.get_video_id(url)
        if video_id:
            metadata = cls.get_metadata(video_id)
            stream_flv_mini_url = metadata.get('url', '')
            return bool(stream_flv_mini_url)
            
        return False

    def create_kwars(self):
        return {'videoid': self.video_id}

    def set_values(self, video_obj):
        metadata = self.get_metadata(self.video_id)
        video_obj.description = metadata.get('description', u'')
        video_obj.title = metadata.get('title', '')
        video_obj.thumbnail = metadata.get('thumbnail_url') or ''
        return video_obj
    
    @classmethod
    def get_video_id(cls, video_url):
        match = DAILYMOTION_REGEX.match(cls.format_url(video_url))
        return match and match.group(1)
    
    @classmethod
    def get_metadata(cls, video_id):
        #FIXME: get_metadata is called twice: in matches_video_url and set_values
        conn = httplib.HTTPConnection("www.dailymotion.com")
        conn.request("GET", "/json/video/" + video_id)
        try:
            response = conn.getresponse()
            body = response.read()
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                raise VideoTypeError(_(u'Video is unavailable'))
        except httplib.BadStatusLine:
            return {}
