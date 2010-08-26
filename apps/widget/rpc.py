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
from uuid import uuid4
import re
import simplejson as json
import widget
from videos.models import VIDEO_SESSION_KEY
from urlparse import urlparse, parse_qs
from django.conf import settings

LANGUAGES_MAP = dict(LANGUAGES)

def show_widget(request, video_url, null_widget, base_state=None):
    #FIXME: shorten this method.
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
    # video_tab corresponds to mirosubs.widget.VideoTab.InitialState in
    # javascript.
    video_tab = 0
    if null_widget:
        null_subtitles = None
        if request.user.is_authenticated:
            null_subtitles = video.null_subtitles(request.user)
            translation_language_codes = \
                video.null_translation_language_codes(request.user)
        else:
            translation_language_codes = []
        if null_subtitles is None:
            video_tab = 0
        else:
            video_tab = 1
    else:
        translation_language_codes = video.translation_language_codes()
        if video.subtitle_state == models.NO_SUBTITLES:
            video_tab = 0
        else:
            video_tab = 1
    return_value['initial_tab'] = video_tab
    return_value['translation_languages'] = \
        [widget.language_to_map(code, LANGUAGES_MAP[code]) for 
         code in translation_language_codes]
    if base_state is not None:
        return_value['subtitles'] = _autoplay_subtitles(
            request, video, null_widget, 
            base_state.get('language', None),
            base_state.get('revision', None))
    if request.user.is_authenticated:
        return_value['username'] = request.user.username
    return_value['embed_version'] = settings.EMBED_JS_VERSION
    return return_value

def start_editing(request, video_id, language_code=None, editing=False):
    """Called by subtitling widget when subtitling or translation 
    is to commence or recommence on a video.
    """

    _maybe_add_video_session(request)

    language = _get_language_for_editing(request, video_id, language_code)

    if language is None:
        return { "can_edit": False, 
                 "locked_by" : language.writelock_owner_name }

    version = _get_version_for_editing(request.user, language)

    existing_subtitles = \
        [s.to_json_dict(is_dependent_translation=language_code is not None)
         for s in version.subtitle_set.all()]

    return_dict = { "can_edit" : True,
                    "version" : version.version_no,
                    "existing" : existing_subtitles }
    if editing and language_code is not None:
        return_dict['existing_captions'] = \
            fetch_subtitles(request, video_id)
        return_dict['languages'] = \
            [widget.language_to_map(lang[0], lang[1]) 
             for lang in LANGUAGES]
    return return_dict

def update_lock(request, video_id, language_code=None):
    language = models.Video.objects.get(
        video_id=video_id).subtitle_language(language_code)
    if language.can_writelock(request):
        language.writelock(request)
        language.save()
        return { "response" : "ok" }
    else:
        return { "response" : "failed" }        

def release_lock(request, video_id, language_code=None):
    language = models.Video.objects.get(
        video_id=video_id).subtitle_language(language_code)
    if language.can_writelock(request):
        language.release_writelock()
        language.save()
    return { "response": "ok" }

def get_my_user_info(request):
    if request.user.is_authenticated():
        return { "logged_in" : True,
                 "username" : request.user.username }
    else:
        return { "logged_in" : False }

def save_subtitles(request, video_id, deleted, inserted, updated, language_code=None):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }

    language = models.Video.objects.get(
        video_id=video_id).subtitle_language(language_code)
    if not language.can_writelock(request):
        return { "response" : "unlockable" }
    language.writelock(request)
    _save_subtitles_impl(request, language, deleted, inserted, updated)
    return {"response" : "ok"}

def finished_subtitles(request, video_id, deleted, inserted, updated, language_code=None):
    language = models.Video.objects.get(
        video_id=video_id).subtitle_language(language_code)
    if not language.can_writelock(request):
        return { "response" : "unlockable" }
    _save_subtitles_impl(request, language, deleted, inserted, updated)
    last_version = language.latest_version()
    if last_version is not None:
        last_version.finished = True
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

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}

def fetch_subtitles(request, video_id, language_code=None):
    video = models.Video.objects.get(video_id=video_id)
    video.subtitles_fetched_count += 1
    video.save()
    if language_code is None:
        return [s.to_json_dict() for s in video.latest_finished_subtitles()]
    else:
        return [s[0].to_json_dict(text_to_use=s[1].subtitle_text)
                for s in video.dependent_translations(language_code)]

def fetch_captions_and_open_languages(request, video_id):
    return { 'captions': fetch_captions(request, video_id),
             'languages': [widget.language_to_map(lang[0], lang[1]) 
                           for lang in LANGUAGES]}

def _save_subtitles_impl(request, language, deleted, inserted, updated):
    if language.video.owner is None:
        language.video.owner = request.user
        language.video.save()
    if len(deleted) == 0 and len(inserted) == 0 and len(updated) == 0:
        return None
    current_version = language.latest_version()
    _apply_subtitle_changes(
        current_version.subtitle_set, deleted, inserted, 
        updated, current_version, is_dependent_translation=not language.is_original)
    current_version.save()

def _apply_subtitle_changes(subtitle_set, deleted, inserted, updated, 
                            version, is_dependent_translation=False):
    for d in deleted:
        subtitle_set.remove(subtitle_set.get(subtitle_id=d['caption_id']))
    for u in updated:
        subtitle = subtitle_set.get(subtitle_id=u['caption_id'])
        subtitle.update_from(u, is_dependent_translation)
        subtitle.save()
    for i in inserted:
        if is_dependent_translation:
            subtitle = models.Subtitle(
                subtitle_id=i['caption_id'],
                subtitle_text=i['text'])
        else:
            subtitle = models.Subtitle(
                version=version,
                subtitle_id=i['caption_id'],
                subtitle_text=i['caption_text'],
                start_time=i['start_time'],
                end_time=i['end_time'],
                subtitle_order=i['sub_order'])
        subtitle_set.add(subtitle)

def _get_version_for_editing(user, language):
    subtitle_versions = list(language.subtitleversion_set.order_by('-version_no'))
    is_new_version = True
    last_version = None
    if len(subtitle_versions) == 0:
        new_version_no = 0
    else:
        last_version = subtitle_versions[0]
        if last_version.finished:
            new_version_no = last_version.version_no + 1
        else:
            if not user.is_anonymous() and \
                    last_version.user.pk == user.pk:
                is_new_version = False
            elif len(subtitle_versions) > 1:
                last_version = subtitle_versions[1]
                new_version_no = last_version.version_no + 1
                subtitle_versions[0].delete()
            else:
                last_version = None
                new_version_no = 0
                subtitle_versions[0].delete()
    if is_new_version:
        new_version = models.SubtitleVersion(
            language=language,
            version_no=new_version_no,
            datetime_started=datetime.now(),
            user=user)
        new_version.save()
        if last_version is not None:
            for subtitle in last_version.subtitle_set.all():
                new_version.subtitle_set.add(subtitle.duplicate_for(new_version))
    return new_version if is_new_version else last_version

def _get_language_for_editing(request, video_id, language_code):
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
        return None
    language.writelock(request)
    language.save()
    return language

def _maybe_add_video_session(request):
    if VIDEO_SESSION_KEY not in request.session:
        request.session[VIDEO_SESSION_KEY] = str(uuid4()).replace('-', '')

def _autoplay_subtitles(request, video, null_widget, language, revision):
    params = { }
    video.subtitles_fetched_count += 1
    video.save()
    if language is not None:
        if null_widget:
            translations = \
                video.null_captions_and_translations(
                request.user, language)
        else:
            translations = \
                video.captions_and_translations(language, revision)
        return [t[0].to_json_dict(
                None if t[1] is None else t[1].translation_text)
                for t in translations]
    else:
        if null_widget:
            subtitles = list(video.null_captions(
                    request.user).videocaption_set.all())
        else:
            caption_version = video.captions(revision)
            subtitles = [] if caption_version is None else list(caption_version.videocaption_set.all())
        return [subtitle.to_json_dict() 
                for subtitle in subtitles]
