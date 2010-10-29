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

from django.conf.global_settings import LANGUAGES
from videos import models
from datetime import datetime
import re
import simplejson as json
import widget
from widget.base_rpc import BaseRpc
from videos.models import VIDEO_SESSION_KEY
from urlparse import urlparse, parse_qs
from django.conf import settings
from django.db.models import Sum

LANGUAGES_MAP = dict(LANGUAGES)

class Rpc(BaseRpc):
    def show_widget(self, request, video_url, is_remote, base_state=None):
        video, create = models.Video.get_or_create_for_url(video_url)
        video.widget_views_count += 1
        video.save()

        self._maybe_add_video_session(request)

        return_value = {
            'video_id' : video.video_id,
            'writelock_expiration' : models.WRITELOCK_EXPIRATION,
            'embed_version': settings.EMBED_JS_VERSION,
            'languages': LANGUAGES,
            'metadata_languages': settings.METADATA_LANGUAGES
            }
        if request.user.is_authenticated():
            return_value['username'] = request.user.username

        if video.video_type == models.VIDEO_TYPE_BLIPTV:
            return_value['flv_url'] = video.bliptv_flv_url
        return_value['drop_down_contents'] = \
            self._drop_down_contents(request.user, video)

        if base_state is not None:
            subtitles = self._autoplay_subtitles(
                request.user, video, 
                base_state.get('language', None),
                base_state.get('revision', None))
            return_value['subtitles'] = subtitles
        else:
            if is_remote:
                autoplay_language = self._find_remote_autoplay_language(request)
                if autoplay_language is not None:
                    subtitles = self._autoplay_subtitles(
                        request.user, video, autoplay_language, None)
                    return_value['subtitles'] = subtitles
        return return_value

    def start_editing(self, request, video_id, language_code, 
                      original_language_code=None,
                      base_version_no=None, fork=False):
        """Called by subtitling widget when subtitling or translation 
        is to commence or recommence on a video.
        """
        self._maybe_add_video_session(request)
        if original_language_code:
            self._save_original_language(video_id, original_language_code)
        language, can_writelock = self._get_language_for_editing(
            request, video_id, language_code)
        if not can_writelock:
            return { "can_edit": False, 
                     "locked_by" : language.writelock_owner_name }
        draft = self._get_draft_for_editing(
            request, language, base_version_no, fork)
        subtitles = self._subtitles_dict(draft)
        return_dict = { "can_edit" : True,
                        "draft_pk" : draft.pk,
                        "subtitles" : subtitles }
        if draft.is_dependent():
            video = models.Video.objects.get(video_id=video_id)
            return_dict['original_subtitles'] = \
                self._subtitles_dict(video.latest_version())
        return return_dict

    def release_lock(self, request, draft_pk):
        language = models.SubtitleDraft.objects.get(pk=draft_pk).language
        if language.can_writelock(request):
            language.release_writelock()
            language.save()
        return { "response": "ok" }

    def save_subtitles(self, request, draft_pk, packets):
        draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        if not draft.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not draft.matches_request(request):
            return { "response" : "does not match request" }
        draft.language.writelock(request)
        self._save_packets(draft, packets)
        return {"response" : "ok", 
                "last_saved_packet": draft.last_saved_packet}

    def finished_subtitles(self, request, draft_pk, packets):
        draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        if not request.user.is_authenticated():
            return { 'response': 'not_logged_in' }
        if not draft.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not draft.matches_request(request):
            return { "response" : "does not match request" }

        self._save_packets(draft, packets)

        new_version, new_subs = self._create_version_from_draft(draft, request.user)
        if len(new_subs) == 0 and draft.language.latest_version() is None:
            should_save = False
        else:
            should_save = new_version.time_change > 0 or new_version.text_change > 0
        if should_save:
            new_version.save()
            for subtitle in new_subs:
                subtitle.version = new_version
                subtitle.save()
            language = new_version.language
            language.update_complete_state()
            language.is_forked = new_version.is_forked
            language.release_writelock()
            language.save()
            if language.is_original:
                language.video.update_complete_state()
            from videos.models import Action
            Action.create_caption_handler(new_version)

        return { "response" : "ok",
                 "last_saved_packet": draft.last_saved_packet,
                 "drop_down_contents" : 
                     self._drop_down_contents(
                         request.user, draft.video) }

    def _create_version_from_draft(self, draft, user):
        version = models.SubtitleVersion(
            language=draft.language,
            version_no=draft.version_no,
            is_forked=draft.is_forked,
            datetime_started=draft.datetime_started,
            user=user)
        subtitles = models.Subtitle.trim_list(
            [s.duplicate_for() for s in draft.subtitle_set.all()])
        version.set_changes(draft.parent_version, subtitles)
        return version, subtitles

    def fetch_subtitles(self, request, video_id, language_code=None):
        video = models.Video.objects.get(video_id=video_id)
        video.subtitles_fetched_count += 1
        video.save()
        return self._subtitles_dict(video.version(language_code=language_code))

    def get_widget_info(self, request):
        return {
            'all_videos': models.Video.objects.count(),
            'subtitles_fetched_count': models.Video.objects.aggregate(s=Sum('subtitles_fetched_count'))['s'],
            'videos_with_captions': models.Video.objects.exclude(subtitlelanguage=None).count(),
            'translations_count': models.SubtitleLanguage.objects.filter(is_original=False).count()
        }
    
    def _get_draft_for_editing(self, request, language, 
                               base_version_no=None, 
                               fork=False):
        if base_version_no is None:
            draft = self._find_existing_draft_to_edit(
                request, language)
            if draft:
                draft.last_saved_packet = 0
                draft.save()
                return draft

        version_to_copy = language.version(base_version_no)
        draft = models.SubtitleDraft(
            language=language,
            parent_version=version_to_copy,
            datetime_started=datetime.now())
        if fork or (version_to_copy is not None and 
                    version_to_copy.is_forked):
            draft.is_forked = True
        if request.user.is_authenticated():
            draft.user = request.user
        draft.browser_id = request.browser_id
        draft.last_saved_packet = 0
        draft.save()

        if version_to_copy is not None:
            if not version_to_copy.is_forked and fork:
                subs_to_copy = version_to_copy.subtitles()
            else:
                subs_to_copy = version_to_copy.subtitle_set.all()
            for subtitle in subs_to_copy:
                draft.subtitle_set.add(subtitle.duplicate_for(draft=draft))
        return draft

    def _find_existing_draft_to_edit(self, request, language):
        latest_version = language.latest_version()
        draft = None
        if request.user.is_authenticated():
            try:
                draft = models.SubtitleDraft.objects.get(
                    language=language, 
                    parent_version=latest_version,
                    user=request.user)
            except:
                pass
        if not draft:
            try:
                draft = models.SubtitleDraft.objects.get(
                    langauge=language,
                    parent_version=latest_version,
                    browser_id=request.browser_id)
            except:
                pass
        return draft

    def _get_language_for_editing(self, request, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        if language_code is None:
            language, created = models.SubtitleLanguage.objects.get_or_create(
                video=video,
                is_original=True,
                defaults = {
                    'writelock_session_key': '',
                    'language': ''
                    })
        else:
            language, created = models.SubtitleLanguage.objects.get_or_create(
                video=video,
                language=language_code,
                defaults={
                    'writelock_session_key': ''
                    })
        if not language.can_writelock(request):
            return language, False
        language.writelock(request)
        language.save()
        return language, True

    def _save_original_language(self, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        existing_language, created = \
            models.SubtitleLanguage.objects.get_or_create(
                video=video,
                language=language_code,
                defaults={'writelock_session_key': ''})
        if not existing_language.is_original:
            original_language = video.subtitle_language()
            if original_language is not None:
                original_language.is_original = False
                original_language.save()
            existing_language.is_original = True
            existing_language.save()

    def _autoplay_subtitles(self, user, video, language_code, version_no):
        if video.subtitle_language(language_code) is None:
            return None
        video.subtitles_fetched_count += 1
        video.save()
        version = video.version(version_no, language_code)
        if version:
            return self._subtitles_dict(version)

    def _subtitles_dict(self, version):
        language = version.language
        is_latest = False
        latest_version = language.latest_version()
        if latest_version is None or version.version_no >= latest_version.version_no:
            is_latest = True
        return self._make_subtitles_dict(
            [s.__dict__ for s in version.subtitles()],
            None if language.is_original else language.language,
            version.version_no,
            is_latest,
            version.is_forked)

    def _subtitle_count(self, user, video):
        version = video.latest_version()
        return 0 if version is None else version.subtitle_set.count()

    def _initial_languages(self, user, video):
        translated_languages = video.subtitlelanguage_set.filter(
            is_complete=True).filter(is_original=False)
        return [(t.language, t.percent_done) for t in translated_languages]
