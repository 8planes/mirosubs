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

from videos.types.base import registrar, VideoType

class HtmlFiveVideoType(VideoType):
    abbreviation = 'H'
    name = 'HTML5'
    _ogg_pattern = r"\.ogv$|\.ogg$"
    _mp4_pattern = r"\.mp4$"
    _webm_pattern = r"\.webm$"

    def video_url(self, video_url_model):
        return video_url_model.video_url

    def matches_video_url(self, parsed_url):
        for pattern in [_ogg_pattern, _mp4_pattern, _webm_pattern]:
            if re.search(pattern, parsed_url.path, re.I) is not None:
                return True
        return False

    def set_values(self, video_model, video_url):
        pass

    def _video_url_kwargs(self, video_url):
        return { 'html5_video_url': video_url }

registrar.register(HtmlFiveVideoType)
