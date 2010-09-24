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
    def start_editing(self, request, video_id, language_code=None, 
                      base_version_no=None, fork=False, editing=False):
        """Called by subtitling widget when subtitling or translation 
        is to commence or recommence on a video.
        """

        self._maybe_add_video_session(request)

        language, can_writelock = self._get_language_for_editing(
            request, video_id, language_code)

        if not can_writelock:
            return { "can_edit": False, 
                     "locked_by" : language.writelock_owner_name }

        version = self._get_version_for_editing(
            request.user, language, base_version_no, fork)

        existing_subtitles = [s.__dict__ for s in version.subtitles()]

        return_dict = { "can_edit" : True,
                        "version" : version.version_no,
                        "existing" : existing_subtitles }
        if editing and language_code is not None:
            return_dict['existing_captions'] = \
                self.fetch_subtitles(request, video_id)
            return_dict['languages'] = \
                [widget.language_to_map(lang[0], lang[1]) 
                 for lang in LANGUAGES]
        return return_dict

    def update_lock(self, request, video_id, language_code=None):
        language = models.Video.objects.get(
            video_id=video_id).subtitle_language(language_code)
        if language.can_writelock(request):
            language.writelock(request)
            language.save()
            return { "response" : "ok" }
        else:
            return { "response" : "failed" }        

    def release_lock(self, request, video_id, language_code=None):
        language = models.Video.objects.get(
            video_id=video_id).subtitle_language(language_code)
        if language.can_writelock(request):
            language.release_writelock()
            language.save()
        return { "response": "ok" }

    def save_subtitles(self, request, video_id, deleted, inserted, updated, language_code=None):
        if not request.user.is_authenticated():
            return { "response" : "not_logged_in" }

        language = models.Video.objects.get(
            video_id=video_id).subtitle_language(language_code)
        if not language.can_writelock(request):
            return { "response" : "unlockable" }
        language.writelock(request)
        self._save_subtitles_impl(request, language, deleted, inserted, updated)
        return {"response" : "ok"}

    def finished_subtitles(self, request, video_id, deleted, inserted, 
                           updated, language_code=None):
        language = models.Video.objects.get(
            video_id=video_id).subtitle_language(language_code)
        if not language.can_writelock(request):
            return { "response" : "unlockable" }
        self._save_subtitles_impl(
            request, language, deleted, inserted, updated)
        last_version = language.latest_version()
        last_version.finished = True
        last_version.user = request.user
        last_version.save()
        language = models.SubtitleLanguage.objects.get(pk=language.pk)
        language.release_writelock()
        language.save()
        return_dict = { "response" : "ok" }
        if language_code is not None:
            return_dict["available_languages"] = \
                [widget.language_to_map(code, LANGUAGES_MAP[code]) for
                 code in language.video.translation_language_codes()]
        return return_dict

    def fetch_subtitles(self, request, video_id, language_code=None):
        video = models.Video.objects.get(video_id=video_id)
        video.subtitles_fetched_count += 1
        video.save()
        return [s.__dict__ for s in video.latest_finished_subtitles(
                language_code=language_code)]

    def fetch_subtitles_and_open_languages(self, request, video_id):
        return { 'captions': self.fetch_subtitles(request, video_id),
                 'languages': [widget.language_to_map(lang[0], lang[1]) 
                               for lang in LANGUAGES]}
    
    def get_widget_info(self, request):
        return {
            'all_videos': models.Video.objects.count(),
            'subtitles_fetched_count': models.Video.objects.aggregate(s=Sum('subtitles_fetched_count'))['s'],
            'videos_with_captions': models.Video.objects.exclude(subtitlelanguage=None).count(),
            'translations_count': models.SubtitleLanguage.objects.filter(is_original=False).count()
        }
    
    def _save_subtitles_impl(self, request, language, deleted, inserted, updated):
        if len(deleted) == 0 and len(inserted) == 0 and len(updated) == 0:
            return
        current_version = language.latest_version()
        self._apply_subtitle_changes(
            current_version, deleted, inserted, updated)
        current_version.save()

    def _get_version_for_editing(self, user, language, 
                                 base_version_no=None, fork=False):
        subtitle_versions = list(language.subtitleversion_set.order_by('-version_no'))

        if base_version_no is None:
            version_to_copy, new_version_no = \
                self._prepare_version_to_edit_latest(user, subtitle_versions)
        else:
            version_to_copy = language.version(base_version_no)
            latest_version = language.latest_version()
            if not latest_version.finished:
                latest_version.delete()
            new_version_no = language.latest_finished_version().version_no + 1

        new_version = None
        if version_to_copy is None or new_version_no > version_to_copy.version_no:
            new_version = models.SubtitleVersion(
                language=language,
                version_no=new_version_no,
                datetime_started=datetime.now())
            if fork or (version_to_copy is not None and 
                        version_to_copy.is_forked):
                new_version.is_forked = True
                if not language.is_forked:
                    language.is_forked = True
                    language.save()
            if user.is_authenticated():
                new_version.user = user
            new_version.save()
            if version_to_copy is not None:
                for subtitle in version_to_copy.subtitle_set.all():
                    new_version.subtitle_set.add(subtitle.duplicate_for(new_version))
        return version_to_copy if new_version is None else new_version

    def _prepare_version_to_edit_latest(self, user, subtitle_versions):
        version_to_copy = None
        if len(subtitle_versions) == 0:
            new_version_no = 0
        else:
            version_to_copy = subtitle_versions[0]
            if version_to_copy.finished:
                new_version_no = version_to_copy.version_no + 1
            else:
                if not user.is_anonymous() and \
                        version_to_copy.user is not None and \
                        version_to_copy.user.pk == user.pk:
                    new_version_no = version_to_copy.version_no                    
                elif len(subtitle_versions) > 1:
                    version_to_copy = subtitle_versions[1]
                    new_version_no = version_to_copy.version_no + 1
                    subtitle_versions[0].delete()
                else:
                    version_to_copy = None
                    new_version_no = 0
                    subtitle_versions[0].delete()
        return version_to_copy, new_version_no

    def _get_language_for_editing(self, request, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        language = video.subtitle_language(language_code)
        if language == None:
            language = models.SubtitleLanguage(
                video=video,
                is_original=(language_code==None),
                language=('' if language_code is None else language_code),
                writelock_session_key='')
            language.save()
        if not language.can_writelock(request):
            return language, False
        language.writelock(request)
        language.save()
        return language, True

    def _autoplay_subtitles(self, user, video, language_code, version_no):
        if video.subtitle_language(language_code) is None:
            return None
        video.subtitles_fetched_count += 1
        video.save()
        return [s.__dict__ for s in video.subtitles(
                version_no=version_no, language_code=language_code)]

    def _subtitle_count(self, user, video):
        version = video.latest_finished_version()
        return 0 if version is None else version.subtitle_set.count()

    def _initial_video_tab(self, user, video):
        return 0 if video.subtitle_state == models.NO_SUBTITLES else 1

    def _initial_languages(self, user, video):
        translated_languages = video.subtitlelanguage_set.filter(
            is_complete=True).filter(is_original=False)
        return [(t.language, t.percent_done) for t in translated_languages]
