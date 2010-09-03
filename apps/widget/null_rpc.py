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

class NullRpc(BaseRpc):
    def start_editing(self, request, video_id, language_code=None, editing=False, base_version_no=None):
        version_no = 0
        if not request.user.is_authenticated():
            subtitles = []
        else:
            video = models.Video.objects.get(video_id=video_id)
            null_subtitles, created = self._get_null_subtitles_for_editing(
                request.user, video)
            subtitles = \
                [s.to_json_dict(is_dependent_translation=
                                language_code is not None) 
                 for s in null_subtitles.subtitle_set.all()]
            version_no = 0 if created else 1
        return_dict = { 'can_edit': True,
                        'version': version_no,
                        'existing': subtitles }
        if editing and language_code is not None:
            return_dict['existing_captions'] = \
                self.fetch_subtitles(video_id, request.user)
            return_dict['languages'] = \
                [widget.language_to_map(lang[0], lang[1])
                 for lang in LANGUAGES]
        return return_dict

    def save_subtitles(self, request, video_id, deleted, inserted, updated, language_code=None):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        null_subtitles, created = self._get_null_subtitles_for_editing(
            request.user, video)
        self._save_subtitles_impl(request, null_subtitles, deleted, inserted, updated)
        return {'response':'ok'}

    def finished_subtitles(self, request, video_id, deleted, inserted, updated, language_code=None):
        return self.save_subtitles(
            request, video_id, version_no, deleted, inserted, updated)

    def fetch_subtitles(self, request, video_id, language_code=None):
        null_subtitles = models.Video.objects.get(
            video_id=video_id).null_subtitles(user, language_code)
        return [s.to_json_dict() for s in null_subtitles.subtitle_set.all()]

    def fetch_subtitles_and_open_languages(self, request, video_id):
        return { 'captions': self.fetch_subtitles(request, video_id),
                 'languages': [widget.language_to_map(lang[0], lang[1]) 
                               for lang in LANGUAGES]}


    def _get_null_subtitles_for_editing(self, user, video):
        null_subtitles = video.null_subtitles(user, language_code)
        created = False
        if null_subtitles is None:
            null_subtitles = models.NullSubtitles(
                video=video,
                language=('' if language_code is None else language_code),
                user=user,
                is_original=(language_code is None))
            null_subtitles.save()
            created = True
        return null_subtitles, created


    def _save_subtitles_impl(self, request, null_subtitles, deleted, inserted, updated):
        self._apply_caption_changes(
            null_captions.videocaption_set, deleted, inserted, 
                              updated, None, null_captions)
        null_captions.save()
        return null_captions

    def _autoplay_subtitles(self, user, video, base_state, language_code, revision_no):
        if langugage_code is not None:
            return [t[0].to_json_dict(text_to_use=t[1].subtitle_text)
                    for t in video.null_dependent_translations(
                    user, language_code)]
        else:
            return [s.to_json_dict() for s in video.null_subtitles(user)]

    def _initial_video_tab(self, user, video):
        null_subtitles = None
        if user.is_authenticated:
            null_subtitles = video.null_subtitles(user)
        return 0 if null_subtitles is None else 1

    def _initial_language_codes(self, user, video):
        if user.is_authenticated:
            return video.null_translation_language_codes(user)
        else:
            return []

