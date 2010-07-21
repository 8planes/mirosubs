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

LANGUAGES_MAP = dict(LANGUAGES)

def show_widget(request, video_url, null_widget, base_state):
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
        null_captions = None
        if request.user.is_authenticated:
            null_captions = video.null_captions(request.user)
            translation_language_codes = \
                video.null_translation_language_codes(request.user)
        else:
            translation_language_codes = []
        if null_captions is None:
            video_tab = 0
        elif not null_captions.is_complete:
            video_tab = 1
        else:
            video_tab = 3
    else:
        translation_language_codes = video.translation_language_codes()
        if video.caption_state == models.NO_CAPTIONS:
            video_tab = 0
        elif video.caption_state == models.CAPTIONS_IN_PROGRESS:
            if request.user.is_authenticated and request.user == video.owner:
                video_tab = 1
            else:
                video_tab = 2
                return_value['owned_by'] = video.owner.username
        else:
            video_tab = 3
    return_value['initial_tab'] = video_tab
    return_value['translation_languages'] = \
        [widget.language_to_map(code, LANGUAGES_MAP[code]) for 
         code in translation_language_codes]
    if base_state is not None:
        return_value['subtitles'] = autoplay_subtitles(
            request, video, null_widget, 
            base_state.get('language', None),
            base_state.get('revision', None))
    if request.user.is_authenticated:
        return_value['username'] = request.user.username
    return return_value

def start_editing(request, video_id, base_version_no=None):
    """Called by subtitling widget when subtitling is to commence or recommence on a video.

    Three cases: either the video is locked, or it is owned by someone else 
    already and doesn't allow community edits, or i can freely edit it."""

    maybe_add_video_session(request)

    video = models.Video.objects.get(video_id=video_id)
    if (not video.allow_community_edits and 
        video.owner != None and (request.user.is_anonymous() or 
                                 video.owner.pk != request.user.pk)):
        return { "can_edit": False, "owned_by" : video.owner.username }
    if not video.can_writelock(request):
        return { "can_edit": False, "locked_by" : video.writelock_owner_name }

    video.writelock(request)
    video.save()
    latest_captions = video.captions()
    if latest_captions is None:
        new_version_no = 0
        existing_captions = []
    else:
        new_version_no = latest_captions.version_no + 1
        existing_captions = \
            list(video.captions(base_version_no).videocaption_set.all())
    return { "can_edit" : True,
             "version" : new_version_no,
             "existing" : [caption.to_json_dict() for 
                           caption in existing_captions] }

def start_editing_null(request, video_id, base_version_no=None):
    # FIXME: note duplication with start_editing, fix that.
    if not request.user.is_authenticated():
        captions = []
    else:
        video = models.Video.objects.get(video_id=video_id)
        null_captions = video.null_captions(request.user)
        if null_captions is None:
            captions = []
            version_no = 0
        else:
            captions = list(null_captions.videocaption_set.all())
            version_no = 1
    return { 'can_edit': True,
             'version': version_no,
             'existing': [caption.to_json_dict() for
                          caption in captions] }

def start_translating(request, video_id, language_code, editing=False, base_version_no=None):
    """Called by widget whenever translating is about to commence or recommence."""

    maybe_add_video_session(request)

    video = models.Video.objects.get(video_id=video_id)
    translation_language = video.translation_language(language_code)
    if translation_language == None:
        translation_language = models.TranslationLanguage(
            video=video,
            language=language_code,
            writelock_session_key='')
        translation_language.save()
    # TODO: note duplication with start_editing. Figure out a way to fix this.
    if not translation_language.can_writelock(request):
        return { "can_edit": False, 
                 "locked_by" : video.writelock_owner_name }
    translation_language.writelock(request)
    translation_language.save()
    latest_translations = translation_language.translations()
    if latest_translations is None:
        new_version_no = 0
        existing_translations = []
    else:
        new_version_no = latest_translations.version_no + 1
        existing_translations = list(
            translation_language.translations(base_version_no).translation_set.all())
    return_dict = { 'can_edit' : True,
                    'version' : new_version_no, 
                    'existing' : [trans.to_json_dict() for 
                                  trans in existing_translations] }
    if editing:
        return_dict['existing_captions'] = fetch_captions(request, video_id)
        return_dict['languages'] = [widget.language_to_map(lang[0], lang[1]) 
                                    for lang in LANGUAGES]
    return return_dict

def start_translating_null(request, video_id, language_code, editing=False, base_version_no=None):
    # FIXME: note duplication with start_translating, fix that.

    maybe_add_video_session(request)

    if not request.user.is_authenticated():
        translations = []
    else:
        video = models.Video.objects.get(video_id=video_id)
        null_translations = video.null_translations(request.user, 
                                                    language_code)
        if null_translations is None:
            translations = []
        else:
            translations = list(null_translations.translation_set.all())
    return_dict = { 'can_edit': True,
                    'version': 0,
                    'existing': [trans.to_json_dict() for
                                 trans in translations] }
    if editing:
        return_dict['existing_captions'] = fetch_captions_null(request, video_id)
        return_dict['languages'] = [widget.language_to_map(lang[0], lang[1])
                                    for lang in LANGUAGES]
    return return_dict

def update_video_lock(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    if video.can_writelock(request):
        video.writelock(request)
        video.save()
        return { "response" : "ok" }
    else:
        return { "response" : "failed" }        

def update_video_translation_lock(request, video_id, language_code):
    translation_language = models.Video.objects.get(
        video_id=video_id).translation_language(language_code)
    if translation_language.can_writelock(request):
        translation_language.writelock(request)
        translation_language.save()
        return { 'response' : 'ok' }
    else:
        return { 'response' : 'failed' }

def release_video_lock(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    if video.can_writelock(request):
        video.release_writelock()
        video.save()
    return { "response": "ok" }

def get_my_user_info(request):
    if request.user.is_authenticated():
        return { "logged_in" : True,
                 "username" : request.user.username }
    else:
        return { "logged_in" : False }

def save_captions(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    if not video.can_writelock(request):
        return { "response" : "unlockable" }
    video.writelock(request)
    save_captions_impl(request, video, version_no, deleted, inserted, updated)
    return {"response" : "ok"}

def save_captions_null(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    save_captions_null_impl(request, video, version_no, deleted, inserted, updated)
    return {'response':'ok'}

def save_translations(request, video_id, language_code, version_no, 
                      inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    translation_language = models.Video.objects.get(
        video_id=video_id).translation_language(language_code)
    if not translation_language.can_writelock(request):
        return { 'response' : 'unlockable' }
    translation_language.writelock(request)
    save_translations_impl(request, translation_language, 
                           version_no, inserted, updated)
    return {'response':'ok'}

def save_translations_null(request, video_id, language_code, 
                           version_no, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    save_translations_null_impl(request, video, language_code, inserted, updated)
    return {'response':'ok'}

def finished_captions(request, video_id, version_no, deleted, inserted, updated):
    video = models.Video.objects.get(video_id=video_id)
    if not video.can_writelock(request):
        return { "response" : "unlockable" }
    last_version = save_captions_impl(request, video, version_no, 
                                      deleted, inserted, updated)
    last_version.is_complete = True
    last_version.save()
    video.release_writelock()
    video.save()
    return { "response" : "ok" }

def finished_captions_null(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    null_captions = save_captions_null_impl(request, video, version_no, 
                                            deleted, inserted, updated)
    null_captions.is_complete = True
    null_captions.save()
    return {'response':'ok'}

def finished_translations(request, video_id, language_code, version_no, 
                          inserted, updated):
    translation_language = models.Video.objects.get(
        video_id=video_id).translation_language(language_code)
    if not translation_language.can_writelock(request):
        return { 'response' : 'unlockable' }
    last_version = save_translations_impl(request, translation_language,
                                          version_no, inserted, updated)
    last_version.is_complete = True
    last_version.save()
    translation_language.release_writelock()
    translation_language.save()
    video = models.Video.objects.get(video_id=video_id)
    return { 'response' : 'ok',
             'available_languages': 
             [widget.language_to_map(code, LANGUAGES_MAP[code]) for
              code in video.translation_language_codes()] }

def finished_translations_null(request, video_id, language_code, version_no, 
                               inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    null_translations = save_translations_null_impl(request, video, language_code, 
                                                    inserted, updated)
    null_translations.is_complete = True
    null_translations.save()
    video = models.Video.objects.get(video_id=video_id)
    return { 'response' : 'ok',
             'available_languages': 
             [widget.language_to_map(code, LANGUAGES_MAP[code]) for
              code in video.null_translation_language_codes(request.user)] }

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}

def fetch_captions(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    video.subtitles_fetched_count += 1
    video.save()
    captions = list(video.captions().videocaption_set.all())
    return [caption.to_json_dict() for caption in captions]

def fetch_captions_null(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    captions = list(video.null_captions(request.user).videocaption_set.all())
    return [caption.to_json_dict() for caption in captions]

def fetch_translations(request, video_id, language_code):
    video = models.Video.objects.get(video_id=video_id)
    video.subtitles_fetched_count += 1
    video.save()    
    return captions_and_translations_dict(
        video.captions_and_translations(language_code))

def fetch_translations_null(request, video_id, language_code):
    video = models.Video.objects.get(video_id=video_id)
    return captions_and_translations_dict(
        video.null_captions_and_translations(request.user, language_code))

def captions_and_translations_dict(captions_and_translations):
    return [s[0].to_json_dict(
            None if s[1] is None else s[1].translation_text)
            for s in captions_and_translations]

def fetch_captions_and_open_languages(request, video_id):
    return { 'captions': fetch_captions(request, video_id),
             'languages': [widget.language_to_map(lang[0], lang[1]) 
                           for lang in LANGUAGES]}

def fetch_captions_and_open_languages_null(request, video_id):
    return { 'captions': fetch_captions_null(request, video_id),
             'languages': [widget.language_to_map(lang[0], lang[1]) 
                           for lang in LANGUAGES]}

def save_captions_impl(request, video, version_no, deleted, inserted, updated):
    if video.owner is None:
        video.owner = request.user
    video.save()
    last_version = video.captions()
    if last_version != None and last_version.version_no >= version_no:
        current_version = last_version
    else:
        current_version = models.VideoCaptionVersion(
            video=video, version_no=version_no, 
            datetime_started=datetime.now(), user=request.user,
            is_complete=False)
        if last_version != None:
            current_version.is_complete = last_version.is_complete
            current_version.save()
            for caption in list(last_version.videocaption_set.all()):
                current_version.videocaption_set.add(
                    caption.duplicate_for(current_version))
        else:
            current_version.save()
    apply_caption_changes(current_version.videocaption_set, deleted, inserted, 
                          updated, current_version)
    current_version.save()
    return current_version

def save_captions_null_impl(request, video, version_no, deleted, inserted, updated):
    null_captions = video.null_captions(request.user)
    if null_captions is None:
        null_captions = models.NullVideoCaptions(video=video,
                                                 user=request.user)
        null_captions.save()
    apply_caption_changes(null_captions.videocaption_set, deleted, inserted, 
                          updated, None, null_captions)
    null_captions.save()
    return null_captions

def apply_caption_changes(caption_set, deleted, inserted, updated, 
                          version=None, null_captions=None):
    for d in deleted:
        caption_set.remove(caption_set.get(caption_id=d['caption_id']))
    for u in updated:
        caption = caption_set.get(caption_id=u['caption_id'])
        caption.update_from(u)
        caption.save()
    for i in inserted:
        vc = models.VideoCaption(caption_id=i['caption_id'],
                                 caption_text=i['caption_text'],
                                 start_time=i['start_time'],
                                 end_time=i['end_time'],
                                 sub_order=i['sub_order'])
        if version is not None:
            vc.version = version
        else:
            vc.null_captions = null_captions
        caption_set.add(vc)

def save_translations_impl(request, translation_language,
                           version_no, inserted, updated):
    last_version = translation_language.translations()
    if last_version != None and last_version.version_no >= version_no:
        current_version = last_version
    else:
        current_version = models.TranslationVersion(language=translation_language, 
                                                    version_no=version_no,
                                                    user=request.user,
                                                    is_complete=False,
                                                    datetime_started=datetime.now())
        if last_version != None:
            current_version.is_complete = last_version.is_complete
            current_version.save()
            for translation in list(last_version.translation_set.all()):
                current_version.translation_set.add(
                    translation.duplicate_for(current_version))
        else:
            current_version.save()
    apply_translation_changes(current_version.translation_set, inserted, 
                              updated, current_version)
    current_version.save()
    return current_version

def save_translations_null_impl(request, video, language_code, inserted, updated):
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

def apply_translation_changes(translations_set, inserted, updated, 
                              version=None, null_translations=None):
    for u in updated:
        translation = translations_set.get(caption_id=u['caption_id'])
        translation.update_from(u)
        translation.save()
    for i in inserted:
        t = models.Translation(caption_id=i['caption_id'],
                               translation_text=i['text'])
        if version is not None:
            t.version = version
        else:
            t.null_translations = null_translations
        translations_set.add(t)

def maybe_add_video_session(request):
    if VIDEO_SESSION_KEY not in request.session:
        request.session[VIDEO_SESSION_KEY] = str(uuid4()).replace('-', '')

def autoplay_subtitles(request, video, null_widget, language, revision):
    params = { }
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
            subtitles = list(video.captions(revision).videocaption_set.all())
        return [subtitle.to_json_dict() 
                for subtitle in subtitles]
