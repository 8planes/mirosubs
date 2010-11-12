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

from widget.srt_subs import GenerateSubtitlesHandler
from utils import render_to_json
from django.utils import simplejson as json
from django.http import HttpResponse
from videos.models import Video
    
@render_to_json
def subtitles(request):
    callback = request.GET.get('callback')
    video_url = request.GET.get('video_url')
    language = request.GET.get('language')
    revision = request.GET.get('revision')
    format = request.GET.get('format', 'json')
    
    if video_url is None:
        return {'is_error': True, 'message': 'video_url not specified' }
    
    video, created = Video.get_or_create_for_url(video_url)
    
    if not video:
        return {'is_error': True, 'message': 'unsuported video url' }
    
    if format == 'json':
        output = [s.for_json() for s in video.subtitles(version_no=revision, language_code = language)]

        if callback:
            result = json.dumps(output)
            return HttpResponse('%s(%s);' % (callback, result), 'text/javascript')
        else:
            return output
    else:    
        handler = GenerateSubtitlesHandler.get(format)
        
        if not handler:
            return {'is_error': True, 'message': 'undefined format' }
        
        subtitles = [s.for_generator() for s in video.subtitles(version_no=revision, language_code = language)]

        h = handler(subtitles, video)
        return HttpResponse(unicode(h))

@render_to_json    
def subtitle_existence(request):
    video_url = request.GET.get('video_url')
    
    if video_url is None:
        return {'is_error': True, 'message': 'video_url not specified' }
    
    video, created = Video.get_or_create_for_url(video_url)
    
    if not video:
        return {'is_error': True, 'message': 'unsuported video url' }
    
    output = []
    
    for item in video.subtitlelanguage_set.all():
        output.append({
            'code': item.language,
            'name': item.get_language_display(),
            'is_original': item.is_original
        })
        
    return output