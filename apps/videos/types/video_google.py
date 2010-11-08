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
from vidscraper.sites import google_video

class GoogleVideoType(VideoType):

    abbreviation = 'G'
    name = 'video.google.com'   

    def convert_to_video_url(self):
        return self.format_url(self.url)
    
    @classmethod
    def matches_video_url(cls, url):
        return bool(google_video.GOOGLE_VIDEO_REGEX.match(url))

    def create_kwars(self):
        return { 'video_url': self.format_url(self.url) }
    
    def set_values(self, video_obj):
        video_obj.title = google_video.scrape_title(self.url)
        raise Warning('GoogleVideoType does not support thumbnail loading')
        return video_obj    