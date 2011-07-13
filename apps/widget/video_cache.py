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

import datetime

from django.core.cache import cache
from videos.types.base import VideoTypeError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.hashcompat import sha_constructor
from videos.types import video_type_registrar
from settings import ALL_LANGUAGES

TIMEOUT = 60 * 60 * 24 * 5 # 5 days

def get_video_id(video_url):
    cache_key = _video_id_key(video_url)
    value = cache.get(cache_key)
    if bool(value):
        return value
    else:
        from videos.models import Video
        try:
            video, create = Video.get_or_create_for_url(video_url)
        except VideoTypeError:
            return None
        
        if not video:
            return None
        
        video_id = video.video_id
        cache.set(cache_key, video_id, TIMEOUT)
        return video_id

def associate_extra_url(video_url, video_id):
    cache_key = _video_id_key(video_url)
    value = cache.get(cache_key)
    if value is None:
        from videos.models import VideoUrl, Video
        vt = video_type_registrar.video_type_for_url(video_url)
        video_url, created = VideoUrl.objects.get_or_create(
            url=vt.convert_to_video_url(),
            defaults={
                'video': Video.objects.get(video_id=video_id),
                'type': vt.abbreviation,
                'videoid': video_id })
        cache.set(cache_key, video_url.videoid, TIMEOUT)

def invalidate_cache(video_id):
    cache.delete(_video_urls_key(video_id))
    try:
        from apps.videos.models import Video
        video = Video.objects.get(video_id=video_id)
        for l in video.subtitlelanguage_set.all():
            cache.delete(_subtitles_dict_key(video_id, l.pk))
    except Video.DoesNotExist:
        pass
    for language in ALL_LANGUAGES:
        cache.delete(_subtitle_language_pk_key(video_id, language[0]))
    cache.delete(_subtitle_language_pk_key(video_id, None))
    cache.delete(_subtitles_dict_key(video_id, None))
    cache.delete(_subtitles_count_key(video_id))
    cache.delete(_video_languages_key(video_id))
    cache.delete(_video_languages_verbose_key(video_id))
    cache.delete(_video_is_moderated_key(video_id))

    from videos.models import Video
    try:
        video = Video.objects.get(video_id=video_id)
        for url in video.videourl_set.all():
            cache.delete(_video_id_key(url.url))
    except Video.DoesNotExist:
        pass

def invalidate_video_id(video_url):
    cache.delete(_video_id_key(video_url))

def on_video_url_save(sender, instance, **kwargs):
    if instance.video_id:
        invalidate_cache(instance.video.video_id)

def _video_id_key(video_url):
    return 'video_id_{0}'.format(sha_constructor(video_url).hexdigest())

def _video_urls_key(video_id):
    return 'widget_video_urls_{0}'.format(video_id)

def _subtitles_dict_key(video_id, language_pk, version_no=None):
    return 'widget_subtitles_{0}{1}{2}'.format(video_id, language_pk, version_no)

def _subtitles_count_key(video_id):
    return "subtitle_count_{0}".format(video_id)

def _video_languages_key(video_id):
    return "widget_video_languages_{0}".format(video_id)

def _video_languages_verbose_key(video_id):
    return "widget_video_languages_verbose_{0}".format(video_id)

def _video_writelocked_langs_key(video_id):
    return "writelocked_langs_{0}".format(video_id)

def _subtitle_language_pk_key(video_id, language_code):
    return "sl_pk_{0}{1}".format(video_id, language_code)

def _video_is_moderated_key(video_id):
    return 'widget_video_is_moderated_{0}'.format(video_id)

def pk_for_default_language(video_id, language_code):
    cache_key = _subtitle_language_pk_key(video_id, language_code)
    value = cache.get(cache_key)
    if value is not None:
        return None if value == 'none' else value
    else:
        from videos.models import Video
        sl = Video.objects.get(video_id=video_id).subtitle_language(
            language_code)
        pk = 'none' if sl is None else sl.pk
        cache.set(cache_key, pk, TIMEOUT)
        return None if sl is None else sl.pk

def get_video_urls(video_id):
    cache_key = _video_urls_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video_urls = [vu.effective_url for vu 
                 in Video.objects.get(video_id=video_id).videourl_set.all()]
        cache.set(cache_key, video_urls, TIMEOUT)
        return video_urls

def get_subtitles_dict(
    video_id, language_pk, version_no, subtitles_dict_fn, is_remote=False):
    cache_key = _subtitles_dict_key(video_id, language_pk, version_no)
    value = cache.get(cache_key)
    if value is not None:
        cached_value = value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        if language_pk is None:
            language = video.subtitle_language()
        else:    
            language = video.subtitlelanguage_set.get(pk=language_pk)
        video.update_subtitles_fetched(language)
        version = video.version(version_no, language, public_only=not is_remote)
        if version:
            cached_value = subtitles_dict_fn(version)
        else:
            cached_value = 0
        cache.set(cache_key, cached_value, TIMEOUT)
    return None if cached_value == 0 else cached_value

def get_video_languages(video_id):
    from apps.widget.rpc import language_summary
    cache_key = _video_languages_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        languages = video.subtitlelanguage_set.filter(has_version=True)

        return_value = [language_summary(l) for l in languages]
        cache.set(cache_key, return_value, TIMEOUT)
        return return_value

def get_video_languages_verbose(video_id, max_items=6):
    # FIXME: we should probably merge a better method with get_video_languages
    # maybe accepting a 'verbose' param?
    cache_key = _video_languages_verbose_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        languages_with_version_total = video.subtitlelanguage_set.filter(has_version=True).order_by('-percent_done')
        total_number = languages_with_version_total.count()
        languages_with_version = languages_with_version_total[:max_items]
        data = { "items":[]}
        if total_number > max_items:
            data["total"] = total_number - max_items
        for lang in languages_with_version:
            # show only with some translation
            if lang.is_dependent():
                data["items"].append({
                    'language_display': lang.language_display(),
                    'percent_done': lang.percent_done ,
                    'language_url': lang.get_absolute_url(),
                    'is_dependent': True,
                })
            else:
                # append to the beggininig of the list as
                # the UI will show this first
                data["items"].insert(0, {
                    'language_display': lang.language_display(),
                    'is_complete': lang.is_complete,
                    'language_url': lang.get_absolute_url(),
                })
        cache.set(cache_key, data, TIMEOUT)
        return data

def get_is_moderated(video_id):
    cache_key = _video_is_moderated_key(video_id)
    value = cache.get(cache_key)
    if value is  None:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        value = video.is_moderated
        cache.set(cache_key, value, TIMEOUT)
    return value
    
        
    
def _writelocked_store_langs(video_id, langs):
    delimiter = ";"
    cache_key = _video_writelocked_langs_key(video_id)
    value = delimiter.join(langs)
    cache.set(cache_key, value, 5 * 60)
    return langs
        
def writelocked_langs(video_id):
    from videos.models import WRITELOCK_EXPIRATION, Video
    delimiter = ";"
    cache_key = _video_writelocked_langs_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        langs = [x for x in value.split(delimiter) if len(x)  > 0]
        return langs
    else:
        treshold = datetime.datetime.now() - datetime.timedelta(seconds=WRITELOCK_EXPIRATION)
        video = Video.objects.get(video_id=video_id)
        langs = list(video.subtitlelanguage_set.filter(writelock_time__gte=treshold))
        value = _writelocked_store_langs(video_id, [x.language for x in langs])
        return value

def writelock_add_lang(video_id, language_code):
    writelocked_langs_clear(video_id)
    langs = writelocked_langs(video_id)
    if not language_code in langs:
        langs.append(language_code)
        _writelocked_store_langs(video_id, langs)
        
def writelock_remove_lang(video_id, language_code):
    langs = writelocked_langs(video_id)
    if language_code in langs:
        langs.remove(language_code)
        _writelocked_store_langs(video_id, langs)

def writelocked_langs_clear(video_id):
    cache_key = _video_writelocked_langs_key(video_id)
    cache.delete(cache_key)
