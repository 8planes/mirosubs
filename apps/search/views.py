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
from search.forms import SearchForm
from django.conf import settings
from utils.translation import get_user_languages_from_request

def index(request):
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    user_langs = get_user_languages_from_request(request)
    
    if 'q' in request.REQUEST:
        form = SearchForm(request.user, user_langs, request.REQUEST)
    else:
        form = SearchForm(request.user, user_langs)
    
    qs = SearchQuerySet().none()
    
    display_mode = 'all'
    
    if form.is_valid():
        qs = form.search_qs(SearchQuerySet().models(Video).load_all())
        display_mode = form.cleaned_data.get('display', 'all')
        
    if settings.HAYSTACK_SEARCH_ENGINE == 'dummy' and settings.DEBUG:
        q = request.REQUEST.get('q', '')
        qs = Video.objects.filter(title__icontains=q)
    
    context = {
        'query': request.REQUEST.get('q', ''),
        'form': form,
        'display_mode': display_mode
    }
        
    return object_list(request, queryset=qs,
                       paginate_by=20,
                       template_name='search/index.html',
                       template_object_name='result',
                       extra_context=context)   