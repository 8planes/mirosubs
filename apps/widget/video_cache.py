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

from django.core.cache import cache
from videos.types.base import VideoTypeError
from django.conf import settings

TIMEOUT = 60 * 60 * 24 * 5 # 5 days

def get_video_id(video_url):
    cache_key = _video_id_key(video_url)
    value = cache.get(cache_key)
    if value is not None:
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

def _invalidate_cache(video_id, language_code=None):
    cache.delete(_video_urls_key(video_id))
    for l in settings.ALL_LANGUAGES:
        cache.delete(_subtitles_dict_key(video_id, l[0]))
    cache.delete(_subtitles_dict_key(video_id, None))
    cache.delete(_subtitles_count_key(video_id))
    cache.delete(_video_languages_key(video_id))

# only used while testing.
def invalidate_video_id(video_url):
    cache.delete(_video_id_key(video_url))

def on_subtitle_language_save(sender, instance, **kwargs):
    _invalidate_cache(instance.video.video_id, instance.language)

def on_subtitle_version_save(sender, instance, **kwargs):
    _invalidate_cache(instance.language.video.video_id,
                      instance.language.language)

def on_video_url_save(sender, instance, **kwargs):
    _invalidate_cache(instance.video.video_id)

def _video_id_key(video_url):
    return 'video_id_{0}'.format(video_url)

def _video_urls_key(video_id):
    return 'widget_video_urls_{0}'.format(video_id)

def _subtitles_dict_key(video_id, language_code, version_no=None):
    return 'widget_subtitles_{0}{1}{2}'.format(video_id, language_code, version_no)

def _subtitles_count_key(video_id):
    return "subtitle_count_{0}".format(video_id)

def _video_languages_key(video_id):
    return "widget_video_languages_{0}".format(video_id)

def get_video_urls(video_id):
    cache_key = _video_urls_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video_urls = \
            [vu.effective_url for vu 
             in Video.objects.get(video_id=video_id).videourl_set.all()]
        cache.set(cache_key, video_urls, TIMEOUT)
        return video_urls

def get_subtitles_dict(
    video_id, language_code, version_no, subtitles_dict_fn):
    cache_key = _subtitles_dict_key(video_id, language_code, version_no)
    value = cache.get(cache_key)
    if value is not None:
        cached_value = value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        video.update_subtitles_fetched(language_code)
        version = video.version(version_no, language_code)
        if version:
            cached_value = subtitles_dict_fn(version)
        else:
            cached_value = 0
        cache.set(cache_key, cached_value, TIMEOUT)
    return None if cached_value == 0 else cached_value

def get_subtitle_count(video_id):
    cache_key = _subtitles_count_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        version = video.latest_version()
        return_value = 0 if version is None else version.subtitle_set.count()
        cache.set(cache_key, return_value, TIMEOUT)
        return cache.get(cache_key)

def get_video_languages(video_id):
    cache_key = _video_languages_key(video_id)
    value = cache.get(cache_key)
    if value is not None:
        return value
    else:
        from videos.models import Video
        video = Video.objects.get(video_id=video_id)
        translated_languages = video.subtitlelanguage_set.filter(
            is_complete=True).filter(is_original=False)
        return_value = [(t.language, t.percent_done) for t in translated_languages]
        cache.set(cache_key, return_value, TIMEOUT)
        return return_value

