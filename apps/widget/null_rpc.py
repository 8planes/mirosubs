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
            null_subtitles = video.null_subtitles(request.user, language_code)
            if null_subtitles is None:
                subtitles = []
            else:
                subtitles = \
                    [s.to_json_dict(is_dependent_translation=
                                    language_code is not None) 
                     for s in null_subtitles.subtitle_set.all()]
                version_no = 1
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

    def save_subtitles(self, request, video_id, version_no, deleted, inserted, updated):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        _save_subtitles_null_impl(request, video, version_no, deleted, inserted, updated)
        return {'response':'ok'}

    def finished_subtitles(self, request, video_id, version_no, deleted, inserted, updated):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        null_captions = save_captions_null_impl(request, video, version_no, 
                                                deleted, inserted, updated)
        null_captions.save()
        null_captions.video.save()
        return { 'response' : 'ok' }

    def finished_translations(self, request, video_id, language_code, version_no, 
                              inserted, updated):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }
        video = models.Video.objects.get(video_id=video_id)
        null_translations = save_translations_null_impl(request, video, language_code, 
                                                        inserted, updated)
        null_translations.save()
        null_translations.language.save()    
        video = models.Video.objects.get(video_id=video_id)
        return { 'response' : 'ok',
                 'available_languages': 
                 [widget.language_to_map(code, LANGUAGES_MAP[code]) for
                  code in video.null_translation_language_codes(request.user)] }

    def _fetch_subtitles(self, video_id, user):
        null_subtitles = models.Video.objects.get(
            video_id=video_id).null_subtitles(user)
        return [s.to_json_dict() for s in null_subtitles.subtitle_set.all()]

    def fetch_translations(self, request, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        return captions_and_translations_dict(
            video.null_captions_and_translations(request.user, language_code))

    def fetch_captions_and_open_languages(self, request, video_id):
        return { 'captions': fetch_captions_null(request, video_id),
                 'languages': [widget.language_to_map(lang[0], lang[1]) 
                               for lang in LANGUAGES]}

    def save_captions_impl(self, request, video, version_no, deleted, inserted, updated):
        null_captions = video.null_captions(request.user)
        if null_captions is None:
            null_captions = models.NullVideoCaptions(video=video,
                                                     user=request.user)
            null_captions.save()
        apply_caption_changes(null_captions.videocaption_set, deleted, inserted, 
                              updated, None, null_captions)
        null_captions.save()
        return null_captions

    def save_translations_impl(self, request, video, language_code, inserted, updated):
        null_translations = video.null_translations(request.user, language_code)
        if null_translations is None:
            null_translations = models.NullTranslations(video=video,
                                                        user=request.user,
                                                        language=language_code)
            null_translations.save()
        apply_translation_changes(null_translations.translation_set, inserted, 
                                  updated, None, null_translations)
        null_translations.save()
        return null_translations

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

