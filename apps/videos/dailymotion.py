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
import httplib
import json

DAILYMOTION_REGEX = re.compile(r'https?://(?:[^/]+[.])?dailymotion.com/video/(?P<video_id>[-0-9a-zA-Z]+)(?:_.*)?')

def get_video_id(video_url):
    return DAILYMOTION_REGEX.match(video_url).group(1)

def get_metadata(video_url):
    video_id = get_video_id(video_url)
    
    conn = httplib.HTTPConnection("www.dailymotion.com")
    conn.request("GET", "/json/video/" + video_id)
    response = conn.getresponse()
    body = response.read()

    return json.loads(body)
