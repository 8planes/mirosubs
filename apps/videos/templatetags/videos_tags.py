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

register = template.Library()

from videos.types import video_type_registrar, VideoTypeError

@register.inclusion_tag('videos/_video.html', takes_context=True)
def render_video(context, video, display_views='total'):
    context['video'] = video
    
    if display_views and hasattr(video, '%s_views' % display_views):
        context['video_views'] = getattr(video, '%s_views' % display_views)
    else:
        context['video_views'] = video.total_views
    
    return context

@register.inclusion_tag('videos/_feature_video.html', takes_context=True)
def feature_video(context, video):
    context['video'] = video
    return context

@register.filter
def is_follower(obj, user):
    #obj is Video or SubtitleLanguage
    if not user.is_authenticated():
        return False
    
    if not obj:
        return False
    
    return obj.followers.filter(pk=user.pk).exists()

@register.simple_tag
def write_video_type_js(video):
    if not video or not bool(video.get_video_url()):
        return 
    try:
        vt = video_type_registrar.video_type_for_url(video.get_video_url())
        if hasattr(vt, "js_url"):
            return '<script type="text/javascript" src="%s"><script/>' % vt.js_url
    except VideoTypeError:    
        return  
    
