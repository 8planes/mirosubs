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

from videos.types.base import VideoType
from vidscraper.sites import blip
from django.utils.html import strip_tags

class BlipTvVideoType(VideoType):

    abbreviation = 'B'
    name = 'Blip.tv'  
    site = 'blip.tv'
    
    def __init__(self, url):
        self.url = url
        self.file_id = self._get_file_id(url)
        self.shortmem = blip.get_shortmem(url)
    
    @property
    def video_id(self):
        return self.file_id
    
    def convert_to_video_url(self):
        return self.scrape_best_file_url()

    @classmethod
    def matches_video_url(cls, url):
        return blip.BLIP_REGEX.match(url)

    def create_kwars(self):
        return {
            'videoid': self.file_id
        }

    def set_values(self, video_obj):
        video_obj.title = unicode(blip.scrape_title(self.url, self.shortmem))
        video_obj.thumbnail = blip.get_thumbnail_url(self.url, self.shortmem)
        #video_obj.description = strip_tags(blip.scrape_description(self.url, self.shortmem))
        return video_obj

    def _get_file_id(self, video_url):
        return blip.BLIP_REGEX.match(video_url).groupdict()['file_id']

    def scrape_best_file_url(self):
        if not hasattr(self, '_file_url'):
            self._file_url = blip.video_file_url(self.file_id)
        return self._file_url

