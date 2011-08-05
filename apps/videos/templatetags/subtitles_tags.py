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

from django import template
from videos.forms import SubtitlesUploadForm, PasteTranscriptionForm, CreateVideoUrlForm
from django.utils.translation import ugettext_lazy as _, ungettext
from django.utils import translation

register = template.Library()

@register.inclusion_tag('videos/_upload_subtitles.html', takes_context=True)
def upload_subtitles(context, video):
    context['video'] = video
    initial = {}
    if context.get('language') and context['language'].language:
        initial['language'] = context['language'].language
    else:
        initial['language'] = translation.get_language()
        
    original_language = video.subtitle_language()
    if original_language and original_language.language:
        initial['video_language'] = original_language.language
    
    context['form'] = SubtitlesUploadForm(context['user'], initial=initial)
    return context

@register.inclusion_tag('videos/_paste_transcription.html', takes_context=True)    
def paste_transcription(context):
    #It is just template of pop-up, you should add link with 'upload-transcript-button' class
    initial = {}
    if context.get('language') and context['language'].language:
        initial['language'] = context['language'].language
    else:
        initial['language'] = translation.get_language()
        
    original_language = context['video'].subtitle_language()
    if original_language and original_language.language:
        initial['video_language'] = original_language.language
                
    context['form'] = PasteTranscriptionForm(context['user'], initial=initial)
    return context

@register.simple_tag
def complete_indicator(language):
    if language.is_original or language.is_forked:
        if language.is_complete and language.subtitle_count > 0:
            return "100 %"
        v = language.version()
        count = v and v.subtitle_set.count() or 0
        return ungettext('%(count)s Line', '%(count)s Lines', count) % {'count': count}
    return '%i %%' % language.percent_done

@register.simple_tag
def complete_color(language):
    if language.is_original or language.is_forked:
        if language.is_complete:
            return 'eighty'
        else:
            return 'full'
    
    val = language.percent_done
    if val >= 95:
        return 'eighty'
    elif val >= 80:
        return 'sixty'
    elif val >= 30:
        return 'fourty'
    else:
        return 'twenty'

@register.inclusion_tag('videos/_video_url_panel.html', takes_context=True)
def video_url_panel(context):
    video = context['video']
    context['form'] = CreateVideoUrlForm(context['user'], initial={'video': video.pk})
    context['video_urls'] = video.videourl_set.all()
    return context

@register.simple_tag
def video_url_count(video):
    return video.videourl_set.count()