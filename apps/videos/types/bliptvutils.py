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

import httplib
from xml.dom import minidom

def video_file_url(file_id):
    rss_path = '/file/%s?skin=rss' % file_id
    conn = httplib.HTTPConnection("blip.tv")
    conn.request("GET", rss_path)
    response = conn.getresponse()
    body = response.read()
    xmldoc = minidom.parseString(body)
    media_content_elements = xmldoc.getElementsByTagName('media:content')
    return _best_flv(media_content_elements) or \
        _best_mp4(media_content_elements) or \
        _best_any(media_content_elements)

def _best_any(media_contents):
    f = lambda c: True
    return _best_by_height(media_contents, f)

def _best_mp4(media_contents):
    f = lambda c: c.getAttribute('type') in ['video/x-m4v', 'video/mp4']
    return _best_by_height(media_contents, f)

def _best_flv(media_contents):
    f = lambda c: c.getAttribute('type') == 'video/x-flv'
    return _best_by_height(media_contents, f)

def _best_by_height(media_contents, type_fn):
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
