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
from haystack.query import SearchQuerySet
from django.views.generic.list_detail import object_list
from videos.models import Video, SubtitleLanguage

def index(request):
    q = request.REQUEST.get('q')
    
    qs = SearchQuerySet().models(Video)
          
    if q:
        qs = qs.auto_query(q).highlight()
        
    context = {
        'query': q
    }
    ordering, order_type = request.GET.get('o'), request.GET.get('ot')
    order_fields = {
        'title': 'title',
    }
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
        context['ordering'], context['order_type'] = ordering, order_type
        
    return object_list(request, queryset=qs,
                       paginate_by=30,
                       template_name='search/index.html',
                       template_object_name='result',
                       extra_context=context)   