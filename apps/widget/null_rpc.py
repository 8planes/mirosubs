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

from widget.base_rpc import BaseRpc
from videos import models
from django.conf import settings
from django.conf.global_settings import LANGUAGES
import widget
from videos.types import video_type_registrar
from videos.types.bliptv import BlipTvVideoType

class NullRpc(BaseRpc):
    def show_widget(self, request, video_url, is_remote, base_state=None):
        return_value = {
            'video_id' : 'abc',
            'writelock_expiration' : models.WRITELOCK_EXPIRATION,
            'embed_version': settings.EMBED_JS_VERSION,
            'languages': LANGUAGES,
            'metadata_languages': settings.METADATA_LANGUAGES
            }
        if request.user.is_authenticated():
            return_value['username'] = request.user.username
        video_type = video_type_registrar.video_type_for_url(video_url)
        if isinstance(video_type, BlipTvVideoType):
            video_urls = video_type.scrape_best_file_url()
        else:
            video_urls = [video_url]
        return_value['video_urls'] = video_urls
        return_value['drop_down_contents'] = \
            self._drop_down_contents(None)
        return return_value

    def start_editing(self, request, video_id, language_code, 
                      original_language_code=None,
                      base_version_no=None, fork=False):
        return {
            "can_edit": True,
            "draft_pk": 1,
            "subtitles": self._subtitles_dict() }

    def save_subtitles(self, request, draft_pk, packets):
        max_packet_no = max([p['packet_no'] for p in packets])
        return {'response':'ok',
                'last_saved_packet': max_packet_no}

    def finished_subtitles(self, request, draft_pk, packets):
        response = self.save_subtitles(
            request, draft_pk, packets)
        if response['response'] == 'ok':
            response['drop_down_contents'] = \
                self._drop_down_contents(None)
        return response

    def fetch_subtitles(self, request, video_id, language_code=None):
        return self._subtitles_dict()

    def _subtitle_count(self, video_id):
        return 0

    def _initial_languages(self, video_id):
        return []

    def _subtitles_dict(self):
        return self._make_subtitles_dict([], None, True, False, 1, True, True, None, "what")
