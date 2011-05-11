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
from videos.types import video_type_registrar

feed_parsers = []

def parse_feed_entry(entry):
    vt, info = None, {}
    
    for parser in feed_parsers:
        vt, info = parser(entry)
        if vt:
            break
    
    return vt, info

class BaseFeedEntryParser(object):
    
    def get_video_type(self, entry):
        raise Exception('Not implemented')
    
    def get_video_info(self, entry):
        raise Exception('Not implemented')
    
    def __call__(self, entry):
        vt = self.get_video_type(entry)
        if vt:
            info = self.get_video_info(entry)
        else:
            info = {}
        return vt, info
    
class LinkFeedEntryParser(BaseFeedEntryParser):
    
    def get_video_type(self, entry):
        vt = None
        try:
            vt = video_type_registrar.video_type_for_url(entry['link'])
        except KeyError:
            pass
        return vt
    
    def get_video_info(self, entry):
        return {}

feed_parsers.append(LinkFeedEntryParser())