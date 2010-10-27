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

    def __init__(self):
        self.abbreviation = 'V'
        self.name = 'Vimeo.com'   

    def convert_to_video_url(self, url):
        id = self._get_vimeo_id(url)
        return 'http://vimeo.com/%s' % id
    
    def video_url(self, obj):
        return 'http://vimeo.com/%s' % obj.vimeo_videoid

    def matches_video_url(self, url):
        return bool(vimeo.VIMEO_REGEX.match(url))

    def create_kwars(self, video_url):
        return { 'vimeo_videoid': self._get_vimeo_id(video_url) }
    
    def _get_vimeo_id(self, video_url):
        return vimeo.VIMEO_REGEX.match(video_url).group(2) 