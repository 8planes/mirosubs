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

class VideoType(object):
    def video_type_pair(self):
        return (self.abbreviation, self.name)

    def video_url_kwargs(self, video_url):
        args = { 'type': self.abbreviation }.update(self._video_url_kwargs(video_url))

    def _video_url_kwargs(self, video_url):
        return {}

class VideoTypeRegistrar(object):
    _video_types = []
    _video_type_pairs = None
    _video_type_dict = None

    @classmethod
    def register(cls, video_type_class):
        VideoType.register(video_type_class)
        cls._video_types.append(video_type_class())

    @classmethod
    def video_type_pairs(cls):
        if cls._video_type_pairs is None:
            cls._video_type_pairs = \
                tuple([(t.abbreviation, t.name) for t in cls._video_types])
        return cls._video_type_pairs

    @classmethod
    def video_type_dict(cls):
        if cls._video_type_dict is None:
            cls._video_type_dict = dict(
                [(t.abbreviation, t) for t in cls._video_types])
        return cls._video_type_dict

    @classmethod
    def video_type_for_abbreviation(cls, abbreviation):
        return cls.video_type_dict()[abbreviation]

    @classmethod
    def video_type_for_url(cls, url):
        for video_type in cls._video_types:
            if video_type.matches_video_url(url):
                return video_type
        return None

registrar = VideoTypeRegistrar()
