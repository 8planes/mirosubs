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
import httplib
from xml.dom import minidom

class BlipTvVideoType(VideoType):

    abbreviation = 'B'
    name = 'Blip.tv'  
    
    def __init__(self, url):
        self.url = url
        self.file_id = self._get_file_id(url)
    
    def convert_to_video_url(self):
        return self.scrape_best_file_url()

    @classmethod
    def matches_video_url(cls, url):
        return blip.BLIP_REGEX.match(url)

    def create_kwars(self):
        return {'bliptv_fileid': self.file_id}

    def set_values(self, video_obj):
        video_obj.title = blip.scrape_title(self.url)
        video_obj.thumbnail = blip.get_thumbnail_url(self.url)
        video_obj.bliptv_flv_url = self.scrape_best_file_url()
        video_obj.video_url = video_obj.bliptv_flv_url
        return video_obj
    
    def _get_file_id(self, video_url):
        return blip.BLIP_REGEX.match(video_url).groupdict()['file_id']

    def scrape_best_file_url(self):
        if not hasattr(self, '_file_url'):
            rss_path = '/file/%s?skin=rss' % self.file_id
            conn = httplib.HTTPConnection("blip.tv")
            conn.request("GET", rss_path)
            response = conn.getresponse()
            body = response.read()
            xmldoc = minidom.parseString(body)
            media_content_elements = xmldoc.getElementsByTagName('media:content')
            best_file = self._best_flv(media_content_elements) or \
                self._best_mp4(media_content_elements) or \
                self._best_any(media_content_elements)
            self._file_url = best_file
        return self._file_url

    def _best_any(self, media_contents):
        f = lambda c: True
        return self._best_by_height(media_contents, f)
    
    def _best_mp4(self, media_contents):
        f = lambda c: c.getAttribute('type') in ['video/x-m4v', 'video/mp4']
        return self._best_by_height(media_contents, f)
    
    def _best_flv(self, media_contents):
        f = lambda c: c.getAttribute('type') == 'video/x-flv'
        return self._best_by_height(media_contents, f)
    
    def _best_by_height(self, media_contents, type_fn):
        best = None
        best_height = None
        HEIGHT = 360
        for content in media_contents:
            height = int(content.getAttribute('height') or 0)
            height_is_best = True if best is None else \
                abs(HEIGHT - height) < abs(HEIGHT - best_height)
            if type_fn(content) and height_is_best:
                best = content
                best_height = height
        return best and best.getAttribute('url')
