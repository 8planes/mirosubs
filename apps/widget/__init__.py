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

from uuid import uuid4
from videos import models as video_models
from django.conf import settings
from django.contrib.sites.models import Site
from django.conf.global_settings import LANGUAGES
import simplejson as json

LANGUAGES_MAP = dict(LANGUAGES)

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def js_context(request, video, null_widget, element_id=None, 
               debug_js=False, autoplay_lang_code=None):
    params = {'uuid': str(uuid4()).replace('-', ''),
              'video_id': video.video_id,
              'video_url': video.video_url,
              'youtube_videoid': video.youtube_videoid,
              'null_widget': 'true' if null_widget else 'false',
              'debug_js': 'true' if debug_js else 'false',
              'writelock_expiration': video_models.WRITELOCK_EXPIRATION
              }
    if autoplay_lang_code is not None:
        params['autoplay_params'] = create_autoplay_params(
            request, video, null_widget, autoplay_lang_code)
        menutext = 'Original'
        if autoplay_lang_code != '':
            menutext = LANGUAGES_MAP[autoplay_lang_code]
        params['autoplay_menutext'] = menutext
    if element_id is not None:
        params['element_id'] = element_id
    if null_widget:
        null_captions = None
        if request.user.is_authenticated:
            null_captions = video.null_captions(request.user)
            translation_language_codes = \
                video.null_translation_language_codes(request.user)
        else:
            translation_language_codes = []
        if null_captions is None:
            params['show_tab'] = 0
        elif not null_captions.is_complete:
            params['show_tab'] = 1
        else:
            params['show_tab'] = 3
    else:
        translation_language_codes = video.translation_language_codes()
        if video.caption_state == video_models.NO_CAPTIONS:
            params['show_tab'] = 0
        elif video.caption_state == video_models.CAPTIONS_IN_PROGRESS:
            if request.user.is_authenticated and request.user == video.owner:
                params['show_tab'] = 1
            else:
                params['show_tab'] = 2
                params['owned_by'] = video.owner.username
        else:
            params['show_tab'] = 3
    params['translation_languages'] = json.dumps(
        [language_to_map(code, LANGUAGES_MAP[code]) for 
         code in translation_language_codes])
    return add_js_files(params)

def create_autoplay_params(request, video, null_widget, autoplay_lang_code):    
    params = { }
    if autoplay_lang_code != '':
        params['language_code'] = autoplay_lang_code
        params['language'] = LANGUAGES_MAP[autoplay_lang_code]
        if null_widget:
            translations = \
                video.null_captions_and_translations(
                request.user, autoplay_lang_code)
        else:
            translations = \
                video.captions_and_translations(autoplay_lang_code)
        params['subtitles'] = \
            [t[0].to_json_dict(
                None if t[1] is None else t[1].translation_text)
             for t in translations]
    else:
        if null_widget:
            subtitles = list(video.null_captions(
                    request.user).videocaption_set.all())
        else:
            subtitles = list(video.captions().videocaption_set.all())
        params['subtitles'] = [subtitle.to_json_dict() 
                               for subtitle in subtitles]
    return json.dumps(params)

def add_js_files(context):
    context["js_use_compiled"] = settings.JS_USE_COMPILED
    if settings.JS_USE_COMPILED:
        # might change in future when using cdn to serve static js
        context["js_dependencies"] = [full_path("mirosubs-compiled.js")]
    else:
        context["js_dependencies"] = [full_path(js_file) for js_file in settings.JS_RAW]
    context["site"] = Site.objects.get_current()
    return context;

def language_to_map(code, name):
    return { 'code': code, 'name': name };
