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
from vidscraper.sites import ustream

class UstreamVideoType(VideoType):

    abbreviation = 'U'
    name = 'Ustream.tv'   
    site = 'ustream.tv'
    
    def __init__(self, url):
        self.url = url
        self.video_url = ustream.get_flash_enclosure_url(url)
    
    def convert_to_video_url(self):
        return self.video_url
    
    @classmethod
    def matches_video_url(cls, url):
        return bool(ustream.USTREAM_REGEX.match(url))

    def create_kwars(self):
        return { 'url': self.video_url }
    
    def set_values(self, video_obj):
        video_obj.title = ustream.get_title(self.url)
        video_obj.description = ustream.get_description(self.url)
        video_obj.thumbnail = ustream.get_thumbnail_url(self.url)
        return video_obj   
