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
from django.conf.global_settings import LANGUAGES
import widget

class NullRpc(BaseRpc):
    def start_editing(self, request, video_id, language_code=None, editing=False, base_version_no=None):
        version_no = 0
        if not request.user.is_authenticated():
            subtitles = []
        else:
            video = models.Video.objects.get(video_id=video_id)
            null_subtitles, created = self._get_null_subtitles_for_editing(
                request.user, video, language_code)
            subtitles = [s.__dict__ for s in null_subtitles.subtitles()]
            version_no = 0 if created else 1
        return_dict = { 'can_edit': True,
                        'version': version_no,
                        'existing': subtitles }
        if editing and language_code is not None:
            return_dict['existing_captions'] = \
                self.fetch_subtitles(request, video_id)
            return_dict['languages'] = \
                [widget.language_to_map(lang[0], lang[1])
                 for lang in LANGUAGES]
        return return_dict

    def save_subtitles(self, request, video_id, deleted, inserted, updated, language_code=None):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        null_subtitles, created = self._get_null_subtitles_for_editing(
            request.user, video, language_code)
        self._save_subtitles_impl(request, null_subtitles, deleted, inserted, updated)
        return {'response':'ok'}

    def finished_subtitles(self, request, video_id, deleted, inserted, updated, language_code=None):
        # there is no concept of "finished" for null subs
        return self.save_subtitles(
            request, video_id, deleted, inserted, updated, language_code)

    def fetch_subtitles(self, request, video_id, language_code=None):
        if request.user.is_anonymous():
            return []
        video = models.Video.objects.get(video_id=video_id)
        null_subs = video.null_subtitles(request.user, language_code)
        return [] if not null_subs \
            else [s.__dict__ for s in null_subs.subtitles()]

    def fetch_subtitles_and_open_languages(self, request, video_id):
        return { 'captions': self.fetch_subtitles(request, video_id),
                 'languages': [widget.language_to_map(lang[0], lang[1]) 
                               for lang in LANGUAGES]}

    def _get_null_subtitles_for_editing(self, user, video, language_code):
        null_subtitles = video.null_subtitles(user, language_code)
        created = False
        if null_subtitles is None:
            null_subtitles = models.NullSubtitles(
                video=video,
                language=('' if language_code is None else language_code),
                is_original=(language_code is None),                
                user=user)
            null_subtitles.save()
            created = True
        return null_subtitles, created

    def _save_subtitles_impl(self, request, null_subtitles, deleted, inserted, updated):
        self._apply_subtitle_changes(
            null_subtitles, deleted, inserted, updated)
        null_subtitles.save()

    def _autoplay_subtitles(self, user, video, language_code, revision_no):
        null_subs = video.null_subtitles(user, language_code)
        if null_subs is None:
            return None
        else:
            return [s.__dict__ for s in null_subs.subtitles()]

    def _subtitle_count(self, user, video):
        null_subs = video.null_subtitles(user)
        return 0 if null_subs is None else null_subs.subtitle_set.count()

    def _initial_video_tab(self, user, video):
        null_subtitles = None
        if user.is_authenticated:
            null_subtitles = video.null_subtitles(user)
        return 0 if null_subtitles is None else 1

    def _initial_languages(self, user, video):
        if user.is_authenticated:
            # we don't calculate percent done for null translations, 
            # so use the answer to everything, 42
            return [(code, 42) for code in video.null_translation_language_codes(user)]
        else:
            return []

