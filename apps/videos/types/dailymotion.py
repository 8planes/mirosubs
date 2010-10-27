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

from base import VideoType
import httplib
from django.utils import simplejson as json
import re

DAILYMOTION_REGEX = re.compile(r'https?://(?:[^/]+[.])?dailymotion.com/video/(?P<video_id>[-0-9a-zA-Z]+)(?:_.*)?')


class DailymotionVideoType(VideoType):

    def __init__(self):
        self.abbreviation = 'D'
        self.name = 'dailymotion.com'   

    def convert_to_video_url(self, url):
        id = self.get_video_id(url)
        return 'http://dailymotion.com/video/%s' % id
    
    def video_url(self, obj):
        return 'http://dailymotion.com/video/%s' % obj.dailymotion_videoid

    def matches_video_url(self, url):
        if DAILYMOTION_REGEX.match(url):
            metadata = self.get_metadata(url)
            stream_flv_mini_url = metadata.get('stream_flv_mini_url', '')
            return bool(stream_flv_mini_url)
            
        return False

    def create_kwars(self, video_url):
        return {'dailymotion_videoid': self.get_video_id(video_url)}

    def set_values(self, video_obj, video_url):
        metadata = self.get_metadata(video_url)
        video_obj.title = metadata.get('title', '')
        video_obj.video_url = video_url
        video_obj.thumbnail = metadata.get('thumbnail_url') or ''        
        return video_obj
    
    def get_video_id(self, video_url):
        match = DAILYMOTION_REGEX.match(video_url)
        return match and match.group(1)
    
    def get_metadata(self, video_url):
        #FIXME: get_metadata is called twice: in matches_video_url and set_values
        video_id = self.get_video_id(video_url)
        
        conn = httplib.HTTPConnection("www.dailymotion.com")
        conn.request("GET", "/json/video/" + video_id)
        response = conn.getresponse()
        body = response.read()
    
        return json.loads(body)    