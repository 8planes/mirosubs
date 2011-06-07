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

import re
import urlparse

import httplib2

from vidscraper.errors import Error as VidscraperError
from base import VideoType, VideoTypeError
from django.conf import settings
from django.utils.html import strip_tags

BRIGHTCOVE_API_KEY = getattr(settings, 'BRIGHTCOVE_API_KEY', None)
BRIGHTCOVE_API_SECRET = getattr(settings, 'BRIGHTCOVE_API_SECRET' , None)

BRIGHTCOVE_REGEXES = [
    r'http://[\w_-]+.brightcove.com/',
    r'http://bcove.me/[\w_-]+',
]
BRIGHTCOVE_REGEXES = [re.compile(x) for x in BRIGHTCOVE_REGEXES]

class BrightcoveVideoType(VideoType):

    abbreviation = 'C'
    name = 'Brightcove'   
    site = 'brightcove.com'
    js_url = "http://admin.brightcove.com/js/BrightcoveExperiences_all.js"
    
    def __init__(self, url):
        self.url = self._resolve_url_redirects(url)
        self.id = self._get_brightcove_id(self.url)
        try:
            self.shortmem = {}
        except VidscraperError, e:
            raise VideoTypeError(e[0])
        
    def get_video_data(self):
        return {}

    def _resolve_url_redirects(self, url):
        # brighcove service  does not redirect HEAD requests as it should
        h = httplib2.Http()
        resp, content = h.request(url, "GET")
        return resp.get("content-location", url)

    @property
    def video_id(self):
        return self.id
    
    def convert_to_video_url(self):
        return self.url 

    @classmethod    
    def video_url(cls, obj):
        return str(obj)
    
    @classmethod
    def matches_video_url(cls, url):
        if bool(url):
            for r in BRIGHTCOVE_REGEXES:
                if bool(r.match(url)):
                    return True
        return False

    def create_kwars(self):
        return { 'videoid': self.id }
    
    def set_values(self, video_obj):
        # FIXME:
        # brighcove api is not available until you spend at least 499 / month. ?!
        # maybe we can grab this over the client and send it to the backend?
        return video_obj
    
    def _get_brightcove_id(self, video_url):
        try:
            return urlparse.parse_qs(getattr(
                    urlparse.urlparse(video_url), "query", {})).get("bctid", )[0]
        except (KeyError, IndexError):
            return None

