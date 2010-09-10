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
from django.conf import settings
from videos.models import VIDEO_SESSION_KEY
from uuid import uuid4
import widget

LANGUAGES_MAP = dict(LANGUAGES)

class BaseRpc:
    def show_widget(self, request, video_url, base_state=None):
        owner = request.user if request.user.is_authenticated() else None
        video, created = models.Video.get_or_create_for_url(video_url, owner)
        video.widget_views_count += 1
        video.save()

        return_value = {
            'video_id' : video.video_id,
            'writelock_expiration' : models.WRITELOCK_EXPIRATION 
            }
        if video.video_type == models.VIDEO_TYPE_BLIPTV:
            return_value['flv_url'] = video.bliptv_flv_url
        return_value['initial_tab'] = \
            self._initial_video_tab(request.user, video)
        translation_languages = \
            self._initial_languages(request.user, video)
        return_value['translation_languages'] = \
            [widget.language_to_map(t[0], LANGUAGES_MAP[t[0]], percent_done=t[1]) for 
             t in translation_languages]
        if base_state is not None:
            return_value['subtitles'] = self._autoplay_subtitles(
                request.user, video, 
                base_state.get('language', None),
                base_state.get('revision', None))
        else:
            return_value['subtitle_count'] = self._subtitle_count(
                request.user, video)
        if request.user.is_authenticated():
            return_value['username'] = request.user.username
        return_value['embed_version'] = settings.EMBED_JS_VERSION
        return return_value

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

    def _apply_subtitle_changes(self, subtitle_set, deleted, inserted, updated, 
                                is_dependent_translation=False):
        for d in deleted:
            subtitle_set.remove(subtitle_set.get(subtitle_id=d['caption_id']))
        for u in updated:
            subtitle = subtitle_set.get(subtitle_id=u['caption_id'])
            subtitle.update_from(u, is_dependent_translation)
            subtitle.save()
        for i in inserted:
            if not subtitle_set.filter(subtitle_id=i['caption_id']).exists():
                if is_dependent_translation:
                    subtitle = models.Subtitle(
                        subtitle_id=i['caption_id'],
                        subtitle_text=i['text'])
                else:
                    subtitle = models.Subtitle(
                        subtitle_id=i['caption_id'],
                        subtitle_text=i['caption_text'],
                        start_time=i['start_time'],
                        end_time=i['end_time'],
                        subtitle_order=i['sub_order'])
                subtitle_set.add(subtitle)
