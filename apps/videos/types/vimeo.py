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
from base import VideoType

class VimeoVideoType(VideoType):

    abbreviation = 'V'
    name = 'Vimeo.com'   
    
    def __init__(self, url):
        self.url = url
        self.id = self._get_vimeo_id(url)
    
    def convert_to_video_url(self):
        return 'http://vimeo.com/%s' % self.id

    @classmethod    
    def video_url(cls, obj):
        return 'http://vimeo.com/%s' % obj.vimeo_videoid
    
    @classmethod
    def matches_video_url(cls, url):
        return bool(vimeo.VIMEO_REGEX.match(url))

    def create_kwars(self):
        return { 'vimeo_videoid': self.id }
    
    #def set_values(self, video_obj):
    #    video_obj.thumbnail = vimeo.get_thumbnail_url(self.url)
    #    video_obj.save()
    
    def _get_vimeo_id(self, video_url):
        return vimeo.VIMEO_REGEX.match(video_url).group(2) 