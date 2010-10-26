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
    def start_editing(self, request, video_id, language_code, 
                      original_language_code=None,
                      base_version_no=None, fork=False):
        version_no = 0
        null_subtitles = None
        video = models.Video.objects.get(video_id=video_id)
        if not request.user.is_authenticated():
            subtitles = self._make_subtitles_dict(
                [], language_code, 0, True, fork)
            null_placeholder, created = \
                models.NullSubtitlesPlaceholder.objects.get_or_create(
                video=video,
                video_session=self._video_session_key(request),
                defaults={'original_language': original_language_code})
            if not created:
                null_placeholder.original_language = original_language_code
                null_placeholder.save()
        else:
            null_subtitles, created = self._get_null_subtitles_for_editing(
                request.user, video, language_code, 
                original_language_code, fork)
            subtitles = self._subtitles_dict(
                null_subtitles, 0 if created else 1)
        return_dict = { 'can_edit': True,
                        'subtitles': subtitles }
        if null_subtitles and null_subtitles.is_dependent():
            return_dict['original_subtitles'] = \
                self.fetch_subtitles(request, video_id)
        return return_dict

    def save_subtitles(self, request, video_id, packets, language_code=None):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        original_language_code = None

        if video.null_subtitles(request.user, language_code) is None:
            null_placeholder = models.NullSubtitlesPlaceholder.objects.get(
                video=video, 
                video_session=self._video_session_key(request))
            original_language_code = null_placeholder.original_language
        null_subtitles, created = self._get_null_subtitles_for_editing(
            request.user, video, language_code, 
            original_language_code, False)
        self._save_packets(null_subtitles, packets)
        return {'response':'ok',
                'last_saved_packet': null_subtitles.last_saved_packet}

    def finished_subtitles(self, request, video_id, packets, language_code=None):
        # there is no concept of "finished" for null subs
        response = self.save_subtitles(
            request, video_id, packets, language_code)
        if response['response'] == 'ok':
            video = models.Video.objects.get(video_id=video_id)
            response['drop_down_contents'] = \
                self._drop_down_contents(request.user, video)
        return response

    def fetch_subtitles(self, request, video_id, language_code=None):
        if request.user.is_anonymous():
            return []
        video = models.Video.objects.get(video_id=video_id)
        null_subs = video.null_subtitles(request.user, language_code)
        if null_subs:
            return self._subtitles_dict(null_subs, 0)
        else:
            return self._make_subtitles_dict(
                [], language_code, 0, True, True)

    def _get_null_subtitles_for_editing(self, user, video, language_code, original_language_code=None, fork=False):
        orig_created = False
        if original_language_code is not None:
            orig_null_subs, orig_created = \
                models.NullSubtitles.objects.get_or_create(
                    video=video,
                    user=user,
                    is_original=True,
                    defaults={ 'language': original_language_code })
            if not orig_created and orig_null_subs.language != original_language_code:
                orig_null_subs.language = original_language_code
                orig_null_subs.save()
        null_subtitles = video.null_subtitles(user, language_code)
        created = orig_created and language_code == original_language_code
        if null_subtitles is None:
            null_subtitles = models.NullSubtitles(
                video=video,
                language=language_code,
                is_original=False,
                user=user)
            if fork:
                null_subtitles.is_forked = True
            null_subtitles.save()
            created = True
        null_subtitles.last_saved_packet = 0
        return null_subtitles, created

    def _save_subtitles_impl(self, request, null_subtitles, deleted, inserted, updated):
        self._apply_subtitle_changes(
            null_subtitles, deleted, inserted, updated)
        null_subtitles.save()

    def _autoplay_subtitles(self, user, video, language_code, revision_no):
        null_subs = video.null_subtitles(user, language_code)
        if null_subs:
            return self._subtitles_dict(null_subs, 1)

    def _subtitle_count(self, user, video):
        if user.is_authenticated():
            null_subs = video.null_subtitles(user)
            return 0 if null_subs is None else null_subs.subtitle_set.count()
        else:
            return 0

    def _initial_languages(self, user, video):
        if user.is_authenticated():
            # we don't calculate percent done for null translations, 
            # so use the answer to everything, 42
            return [(code, 42) for code in video.null_translation_language_codes(user)]
        else:
            return []

    def _subtitles_dict(self, null_subtitles, version):
        return self._make_subtitles_dict(
            [s.__dict__ for s in null_subtitles.subtitles()],
            None if null_subtitles.is_original else null_subtitles.language,
            version,
            True,
            null_subtitles.is_forked)
