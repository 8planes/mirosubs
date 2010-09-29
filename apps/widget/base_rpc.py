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
from django.utils import translation
from videos import models
from django.conf import settings
from videos.models import VIDEO_SESSION_KEY
from uuid import uuid4
import widget

LANGUAGES_MAP = dict(LANGUAGES)

class BaseRpc:
    def show_widget(self, request, video_url, is_remote, base_state=None):
        video, created = models.Video.get_or_create_for_url(video_url)
        video.widget_views_count += 1
        video.save()

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

    def _make_subtitles_dict(self, subtitles, language, version, is_latest, is_forked):
        return {
            'subtitles': subtitles,
            'language': language,
            'version': version,
            'is_latest': is_latest,
            'forked': is_forked
            }

    def _drop_down_contents(self, user, video):
        return {
            'translations': self._initial_languages(user, video),
            'subtitle_count': self._subtitle_count(user, video)
            }

    def _find_remote_autoplay_language(self, request):
        language = None
        if request.user.is_anonymous() or request.user.preferred_language == '':
            language = translation.get_language_from_request(request)
        else:
            language = request.user.preferred_language
        return language if language != '' else None

    def get_my_user_info(self, request):
        if request.user.is_authenticated():
            return { "logged_in" : True,
                     "username" : request.user.username }
        else:
            return { "logged_in" : False }

    def logout(self, request):
        from django.contrib.auth import logout
        logout(request)
        return {"respones" : "ok"}

    def _maybe_add_video_session(self, request):
        if VIDEO_SESSION_KEY not in request.session:
            request.session[VIDEO_SESSION_KEY] = str(uuid4()).replace('-', '')

    def _apply_subtitle_changes(self, sub_collection, deleted, inserted, updated):
        subtitle_set = sub_collection.subtitle_set
        for d in deleted:
            subtitle_set.remove(subtitle_set.get(subtitle_id=d['subtitle_id']))
        for u in updated:
            subtitle = subtitle_set.get(subtitle_id=u['subtitle_id'])
            subtitle.update_from(u, sub_collection.is_dependent())
            subtitle.save()
        for i in inserted:
            if not subtitle_set.filter(subtitle_id=i['subtitle_id']).exists():
                if sub_collection.is_dependent():
                    subtitle = models.Subtitle(
                        subtitle_id=i['subtitle_id'],
                        subtitle_text=i['text'])
                else:
                    subtitle = models.Subtitle(
                        subtitle_id=i['subtitle_id'],
                        subtitle_text=i['text'],
                        start_time=i['start_time'],
                        end_time=i['end_time'],
                        subtitle_order=i['sub_order'])
                subtitle_set.add(subtitle)
