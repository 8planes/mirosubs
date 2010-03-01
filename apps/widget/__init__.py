from uuid import uuid4
from videos import models as video_models
from django.conf import settings
from django.contrib.sites.models import Site
from django.conf.global_settings import LANGUAGES
import simplejson as json

LANGUAGES_MAP = dict(LANGUAGES)

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def js_context(request, video, null_widget, debug_js=False):
    params = {'uuid': str(uuid4()).replace('-', ''),
              'video_id': video.video_id,
              'video_url': video.video_url,
              'youtube_videoid': video.youtube_videoid,
              'null_widget': 'true' if null_widget else 'false',
              'debug_js': 'true' if debug_js else 'false',
              'writelock_expiration': video_models.WRITELOCK_EXPIRATION
              }
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
        translation_language_codes = video.translation_language_codes
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
