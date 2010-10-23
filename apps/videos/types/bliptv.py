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
from videos import blip as videos_blip
from vidscraper.sites import blip

class BlipTvVideoType(VideoType):
    abbreviation = 'B'
    name = 'Blip.tv'

    def video_url(self, video_url_model):
        return video_url_model.video_url

    def matches_video_url(self, parsed_url):
        return blip.BLIP_REGEX.match(parsed_url.geturl())

    def set_values(self, video_model, video_url):
        bliptv_fileid = blip.BLIP_REGEX.match(video_url).groupdict()['file_id']
        video_model.title = blip.scrape_title(video_url)
        video_model.thumbnail = blip.get_thumbnail_url(video_url)

    def _video_url_kwargs(self, video_url):
        return { 'bliptv_fileid': blip.BLIP_REGEX.match(video_url).groupdict()['file_id'] }

registrar.register(BlipTvVideoType)
