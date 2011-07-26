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
from django.db.models.query import QuerySet
from django.db.models import Model
from search.forms import SearchForm
from haystack.query import SearchQuerySet
from videos.models import Video

register = template.Library()

@register.inclusion_tag('search/_search_form.html', takes_context=True)
def search_form(context, form=None, simple=False):
    return {
        'simple': simple,
        'form': form or SearchForm()
    }

@register.simple_tag
def load_related_for_result(search_qs):
    #should be fixed in future if result will contain not only Video
    from videos.models import SubtitleLanguage
    
    videos = []
    
    for obj in search_qs:
        if not obj:
            continue
        
        if isinstance(obj, Model):
            videos.append((obj.id, obj))
        else:
            videos.append((obj.object.id, obj.object))
    
    videos = dict(videos)
        
    langs_qs = SubtitleLanguage.objects.select_related('video', 'last_version').filter(video__id__in=videos.keys())

    if videos:
        for v in videos.values():
            v.langs_cache = []

        for l in langs_qs:
            videos[l.video_id].langs_cache.append(l)

    return ''

