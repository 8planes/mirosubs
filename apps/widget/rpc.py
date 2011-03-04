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

from django.db.models import ObjectDoesNotExist
from videos import models
from datetime import datetime
import re
import simplejson as json
import widget
from widget.base_rpc import BaseRpc
from urlparse import urlparse, parse_qs
from django.conf import settings
from django.db.models import Sum
from widget import video_cache
from statistic import widget_views_total_counter
from django.utils.translation import ugettext as _

ALL_LANGUAGES = settings.ALL_LANGUAGES
LANGUAGES_MAP = dict(ALL_LANGUAGES)

def add_general_settings(request, dict):
    dict.update({
            'writelock_expiration' : models.WRITELOCK_EXPIRATION,
            'embed_version': settings.EMBED_JS_VERSION,
            'languages': ALL_LANGUAGES,
            'metadata_languages': settings.METADATA_LANGUAGES
            })
    if request.user.is_authenticated():
        dict['username'] = request.user.username

class Rpc(BaseRpc):
    def show_widget(self, request, video_url, is_remote, base_state=None, additional_video_urls=None):
        video_id = video_cache.get_video_id(video_url)
        if video_id is None: # for example, private youtube video.
            return None

        if additional_video_urls is not None:
            for url in additional_video_urls:
                video_cache.associate_extra_url(url, video_id)

        models.Video.widget_views_counter(video_id).incr()
        widget_views_total_counter.incr()
        
        return_value = {
            'video_id' : video_id,
            }
        add_general_settings(request, return_value)
        if request.user.is_authenticated():
            return_value['username'] = request.user.username

        return_value['video_urls'] = video_cache.get_video_urls(video_id)

        return_value['drop_down_contents'] = \
            self._drop_down_contents(video_id)

        if base_state is not None:
            subtitles = self._autoplay_subtitles(
                request.user, video_id, 
                base_state.get('language', None),
                base_state.get('revision', None))
            return_value['subtitles'] = subtitles
        else:
            if is_remote:
                autoplay_language = self._find_remote_autoplay_language(request)
                if autoplay_language is not None:
                    subtitles = self._autoplay_subtitles(
                        request.user, video_id, autoplay_language, None)
                    return_value['subtitles'] = subtitles
        return return_value

    def fetch_video_id_and_settings(self, request, video_url):
        video_id = video_cache.get_video_id(video_url)
        is_original_language_subtitled = self._subtitle_count(video_id) > 0
        general_settings = {}
        add_general_settings(request, general_settings)
        return {
            'video_id': video_id,
            'is_original_language_subtitled': is_original_language_subtitled,
            'general_settings': general_settings }

    def start_editing(self, request, video_id, language_code, 
                      original_language_code=None,
                      base_version_no=None, fork=False):
        """Called by subtitling widget when subtitling or translation 
        is to commence or recommence on a video.
        """
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

    def fork(self, request, draft_pk):
        draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        if not draft.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not draft.matches_request(request):
            return { "response" : "does not match request" }
        draft.language.writelock(request)
        draft.is_forked = True
        draft.save()
        latest_version = draft.video.latest_version()
        sub_dict = dict([(s.subtitle_id, s) for s 
                         in latest_version.subtitle_set.all()])
        to_delete = []
        for sub in draft.subtitle_set.all():
            if sub.subtitle_id in sub_dict:
                standard_sub = sub_dict[sub.subtitle_id]
                sub.start_time = standard_sub.start_time
                sub.end_time = standard_sub.end_time
                sub.save()
            else:
                to_delete.add(sub)
        for sub in to_delete:
            sub.delete()
        draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        return self._subtitles_dict(draft)
    
    def set_title(self, request, draft_pk, value):
        try:
            draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        except models.SubtitleDraft.DoesNotExist:
            return {"response": "draft does not exist"}
        if not draft.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not draft.matches_request(request):
            return { "response" : "does not match request" }
        draft.language.writelock(request)
        draft.language.save()
        models.SubtitleLanguage.objects.filter(pk=draft.language.pk).update(title=value)
        return {"response" : "ok"}
                    
    def save_subtitles(self, request, draft_pk, packets):
        try:
            draft = models.SubtitleDraft.objects.get(pk=draft_pk)
        except models.SubtitleDraft.DoesNotExist:
            return {"response": "draft does not exist"}
        if not draft.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not draft.matches_request(request):
            return { "response" : "does not match request" }
        draft.language.writelock(request)
        draft.language.save()
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
            new_version.update_percent_done()
            if language.is_original:
                language.video.update_complete_state()
                language.video.save()
            from videos.models import Action
            Action.create_caption_handler(new_version)

        return { "response" : "ok",
                 "last_saved_packet": draft.last_saved_packet,
                 "drop_down_contents" : 
                     self._drop_down_contents(draft.video.video_id) }

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
        return video_cache.get_subtitles_dict(
            video_id, language_code, None,
            lambda version: self._subtitles_dict(version))

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
        try:
            # special case where an original SubtitleLanguage is saved with 
            # blank language.
            original_language = \
                models.SubtitleLanguage.objects.get(
                video__video_id=video_id, 
                is_original=True, language='')
            original_language.language = language_code
            original_language.save()
            return
        except ObjectDoesNotExist:
            pass
        existing_language, created = \
            models.SubtitleLanguage.objects.get_or_create(
                video=video,
                language=language_code,
                defaults={'writelock_session_key': ''})
        if not existing_language.is_original:
            original_language = video.subtitle_language()
            if len(original_language.latest_subtitles()) > 0:
                return
            if original_language is not None:
                original_language.is_original = False
                original_language.save()
            existing_language.is_original = True
            existing_language.save()

    def _autoplay_subtitles(self, user, video_id, language_code, version_no):
        return video_cache.get_subtitles_dict(
            video_id, language_code, version_no, 
            lambda version: self._subtitles_dict(version))

    def _subtitles_dict(self, version):
        language = version.language
        is_latest = False
        latest_version = language.latest_version()
        if latest_version is None or version.version_no >= latest_version.version_no:
            is_latest = True
        return self._make_subtitles_dict(
            [s.__dict__ for s in version.subtitles()],
            language.language,
            language.is_original,
            version.version_no,
            is_latest,
            version.is_forked,
            language.get_title())

    def _subtitle_count(self, video_id):
        return video_cache.get_subtitle_count(video_id)

    def _initial_languages(self, video_id):
        return video_cache.get_video_languages(video_id)
