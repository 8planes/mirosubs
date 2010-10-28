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
from base import VideoTypeRegistrar, VideoTypeError
from youtube import YoutubeVideoType
from bliptv import BlipTvVideoType
from htmlfive import HtmlFiveVideoType
from dailymotion import DailymotionVideoType
from vimeo import VimeoVideoType
from flv import FLVVideoType

video_type_registrar = VideoTypeRegistrar()
video_type_registrar.register(YoutubeVideoType)
video_type_registrar.register(BlipTvVideoType)
video_type_registrar.register(HtmlFiveVideoType)
video_type_registrar.register(DailymotionVideoType)
video_type_registrar.register(VimeoVideoType)
video_type_registrar.register(FLVVideoType)

__all__ = ['VideoTypeError', 'video_type_registrar']