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

from vidscraper.sites import vimeo
from vidscraper.errors import Error as VidscraperError
from base import VideoType, VideoTypeError
from django.conf import settings
from django.utils.html import strip_tags

vimeo.VIMEO_API_KEY = getattr(settings, 'VIMEO_API_KEY')
vimeo.VIMEO_API_SECRET = getattr(settings, 'VIMEO_API_SECRET')

class VimeoVideoType(VideoType):

    abbreviation = 'V'
    name = 'Vimeo.com'   
    site = 'vimeo.com'
    
    def __init__(self, url):
        self.url = url
        self.id = self._get_vimeo_id(url)
        try:
            self.shortmem = vimeo.get_shortmem(url)
        except VidscraperError, e:
            raise VideoTypeError(e[0])   
        
    @property
    def video_id(self):
        return self.id
    
    def convert_to_video_url(self):
        return 'http://vimeo.com/%s' % self.id

    @classmethod    
    def video_url(cls, obj):
        return 'http://vimeo.com/%s' % obj.videoid
    
    @classmethod
    def matches_video_url(cls, url):
        return bool(vimeo.VIMEO_REGEX.match(url))

    def create_kwars(self):
        return { 'videoid': self.id }
    
    def set_values(self, video_obj):
        if vimeo.VIMEO_API_KEY and vimeo.VIMEO_API_SECRET:
            video_obj.thumbnail = vimeo.get_thumbnail_url(self.url, self.shortmem)
            video_obj.title = vimeo.scrape_title(self.url, self.shortmem)
            video_obj.description = strip_tags(vimeo.scrape_description(self.url, self.shortmem))
            video_obj.save()
        return video_obj
    
    def _get_vimeo_id(self, video_url):
        return vimeo.VIMEO_REGEX.match(video_url).groupdict().get('video_id') 