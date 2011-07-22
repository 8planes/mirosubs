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

from utils.rpc import Error, Msg, RpcExceptionEvent, add_request_to_kwargs
from django.conf import settings
from search.forms import SearchForm
from videos.search_indexes import VideoSearchResult, LanguageField
from haystack.query import SearchQuerySet
from videos.models import Video
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from videos.rpc import render_page

class SearchApiClass(object):
    
    def load_languages_faceting(self,  q="", user=None):
        q = q or ""
        video_languages = {}
        languages = {}
                
        if q:
            sqs = SearchQuerySet().models(Video)
    
            facet_data = sqs.facet('video_language').facet('languages').facet_counts()
            
            sqs = SearchForm.apply_query(q, sqs)
            
            for lang, val in facet_data['fields']['video_language']:
                sqs = sqs.query_facet('video_language', lang)
            
            for lang, val in facet_data['fields']['languages']:
                sqs = sqs.query_facet('languages', lang)
                
            facet_data = sqs.facet_counts()
    
            
            for item, val in facet_data['queries'].items():
                t, lang = item.split(':')
                if t == 'video_language_exact':
                    video_languages[LanguageField.convert(lang)] = val
                elif t == 'languages_exact':
                    languages[LanguageField.convert(lang)] = val
            
        return {
            'video_languages': video_languages,
            'languages': languages
        }
    
    @add_request_to_kwargs
    def search(self, rdata, request, user):
        form = SearchForm(request, rdata)
        
        if form.is_valid():
            qs = form.search_qs(SearchQuerySet().result_class(VideoSearchResult) \
                .models(Video))
        else:
            qs = SearchQuerySet().none()    
        
        #result = [item.object for item in qs]
        #qs1 = Video.objects.filter(title__contains=rdata['q'])
        #for o in qs1:
        #    if not o in result:
        #        print o.title
        
        display_views = form.get_display_views()
        return render_page(rdata.get('page', 1), qs, 20, request, display_views=display_views)
    
    
