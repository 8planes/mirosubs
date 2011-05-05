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

register = template.Library()

@register.simple_tag
def load_related_for_result(search_qs):
    #should be fixed in future if result will contain not only Video
    from videos.models import SubtitleLanguage
    
    if not isinstance(search_qs, QuerySet):
        videos = dict((obj.object.id, obj.object) for obj in search_qs)
        langs_qs = SubtitleLanguage.objects.select_related('video', 'last_version').filter(video__id__in=videos.keys())

        if videos:
            for v in videos.values():
                v.langs_cache = []
    
            for l in langs_qs:
                videos[l.video_id].langs_cache.append(l)

    return ''

