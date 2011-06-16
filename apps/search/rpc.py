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
from videos.search_indexes import VideoSearchResult
from haystack.query import SearchQuerySet
from videos.models import Video
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from videos.rpc import render_page

class SearchApiClass(object):
    
    @add_request_to_kwargs
    def search(self, rdata, request, user):
        form = SearchForm(request, rdata)

        if form.is_valid():
            qs = form.search_qs(SearchQuerySet().result_class(VideoSearchResult) \
                .models(Video))
        else:
            qs = SearchQuerySet().none()    
        
        return render_page(rdata.get('page', 1), qs, 20, request)
    
    