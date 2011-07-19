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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from videos.models import Video, SubtitleLanguage
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from utils.rpc import Error, Msg, RpcExceptionEvent, add_request_to_kwargs
from utils.translation import get_user_languages_from_request
from django.template.loader import render_to_string
from django.template import RequestContext
from django.conf import settings
from haystack.query import SearchQuerySet
from videos.search_indexes import VideoSearchResult
from utils.celery_search_index import update_search_index
import datetime

VIDEOS_ON_WATCH_PAGE = getattr(settings, 'VIDEOS_ON_WATCH_PAGE', 15)
VIDEOS_ON_PAGE = getattr(settings, 'VIDEOS_ON_PAGE', 30)

class VideosApiClass(object):
    authentication_error_msg = _(u'You should be authenticated.')
    
    popular_videos_sorts = {
        'week': 'week_views', 
        'month': 'month_views', 
        'year': 'year_views', 
        'total': 'total_views'
    }
    
    def unfeature_video(self, video_id, user):
        if not user.has_perm('videos.edit_video'):
            raise RpcExceptionEvent(_(u'You have not permission'))
        
        try:
            c = Video.objects.filter(pk=video_id).update(featured=None)
        except (ValueError, TypeError):
            raise RpcExceptionEvent(_(u'Incorrect video ID'))
        
        if not c:
            raise RpcExceptionEvent(_(u'Video does not exist'))
        
        return {}    
    
    def feature_video(self, video_id, user):
        if not user.has_perm('videos.edit_video'):
            raise RpcExceptionEvent(_(u'You have not permission'))
        
        try:
            c = Video.objects.filter(pk=video_id).update(featured=datetime.datetime.today())
        except (ValueError, TypeError):
            raise RpcExceptionEvent(_(u'Incorrect video ID'))
                
        if not c:
            raise RpcExceptionEvent(_(u'Video does not exist'))
        
        return {}
    
    def load_video_languages(self, video_id, user):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            video = None
        
        context = {
            'video': video,
            'languages': video.subtitlelanguage_set.filter(subtitle_count__gt=0)
        }
        
        return {
            'content': render_to_string('videos/_video_languages.html', context)
        }
    
    @add_request_to_kwargs
    def load_featured_page(self, page, request, user):
        sqs = SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).order_by('-featured')
        
        return render_page(page, sqs, request=request)    

    @add_request_to_kwargs
    def load_latest_page(self, page, request, user):
        sqs = SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).order_by('-edited')
            
        return render_page(page, sqs, request=request)

    @add_request_to_kwargs
    def load_popular_page(self, page, sort, request, user):
        sort_types = {
            'today': 'today_views',
            'week' : 'week_views', 
            'month': 'month_views', 
            'year' : 'year_views', 
            'total': 'total_views'
        }
        
        sort_field = sort_types.get(sort, 'week_views')
        
        sqs = SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).order_by('-%s' % sort_field)
        
        return render_page(page, sqs, request=request, display_views=sort)

    def _get_volunteer_sqs(self, request, user):
        '''
        Return the search query set for videos which would be relevent to
        volunteer for writing subtitles.
        '''
        user_langs = get_user_languages_from_request(request)

        relevent = SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).filter(video_language__in=user_langs) \
            .filter_or(languages__in=user_langs)

        ## The rest of videos which are NOT relevent
        #rest = SearchQuerySet().result_class(VideoSearchResult) \
            #.models(Video).filter(video_language__in=user_langs) \
            #.filter_or(languages__in=user_langs)

        return relevent

    @add_request_to_kwargs
    def load_featured_page_volunteer(self, page, request, user):
        relevent = self._get_volunteer_sqs(request, user)
        sqs = relevent.order_by('-featured')

        return render_page(page, sqs, request=request)    

    @add_request_to_kwargs
    def load_latest_page_volunteer(self, page, request, user):
        relevent = self._get_volunteer_sqs(request, user)
        sqs = relevent.order_by('-edited')

        return render_page(page, sqs, request=request)

    @add_request_to_kwargs
    def load_popular_page_volunteer(self, page, sort, request, user):

        sort_types = {
            'today': 'today_views',
            'week' : 'week_views', 
            'month': 'month_views', 
            'year' : 'year_views', 
            'total': 'total_views'
        }

        sort_field = sort_types.get(sort, 'week_views')

        relevent = self._get_volunteer_sqs(request, user)
        sqs = relevent.order_by('-%s' % sort_field)

        return render_page(page, sqs, request=request)

    @add_request_to_kwargs
    def load_popular_videos(self, sort, request, user):
        sort_types = {
            'today': 'today_views',
            'week': 'week_views', 
            'month': 'month_views', 
            'year': 'year_views', 
            'total': 'total_views'
        }
        
        if sort in sort_types:
            display_views = sort
            sort_field = sort_types[sort]
        else:
            display_views = 'week'
            sort_field = 'week_views'            

        popular_videos = SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).order_by('-%s' % sort_field)[:5]

        context = {
            'display_views': display_views,
            'video_list': popular_videos
        }
        
        content = render_to_string('videos/_watch_page.html', context, RequestContext(request))
        
        return {
            'content': content
        }

    @add_request_to_kwargs
    def load_popular_videos_volunteer(self, sort, request, user):
        sort_types = {
            'today': 'today_views',
            'week': 'week_views', 
            'month': 'month_views', 
            'year': 'year_views', 
            'total': 'total_views'
        }

        sort_field = sort_types.get(sort, 'week_views')

        relevent = self._get_volunteer_sqs(request, user)

        popular_videos = relevent.order_by('-%s' % sort_field)[:5]

        context = {
            'video_list': popular_videos
        }

        content = render_to_string('videos/_watch_page.html', context, RequestContext(request))

        return {
            'content': content
        }

    def change_title_translation(self, language_id, title, user):
        if not user.is_authenticated():
            return Error(self.authentication_error_msg)
        
        if not title:
            return Error(_(u'Title can\'t be empty'))
        
        try:
            sl = SubtitleLanguage.objects.get(id=language_id)
        except SubtitleLanguage.DoesNotExist:
            return Error(_(u'Subtitle language does not exist'))
        
        if not sl.standard_language_id:
            sl.title = title
            sl.save()
            update_search_index.delay(Video, sl.video_id)
            return Msg(_(u'Title was changed success'))
        else:
            return Error(_(u'This is not forked translation'))
    
    def follow(self, video_id, user):
        if not user.is_authenticated():
            return Error(self.authentication_error_msg)
        
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Error(_(u'Video does not exist.'))
        
        video.followers.add(user)
        
        for l in video.subtitlelanguage_set.all():
            l.followers.add(user)   
        
        return Msg(_(u'You are following this video now.'))
    
    def unfollow(self, video_id, user):
        if not user.is_authenticated():
            return Error(self.authentication_error_msg)
        
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Error(_(u'Video does not exist.'))
        
        video.followers.remove(user)
        
        for l in video.subtitlelanguage_set.all():
            l.followers.remove(user)        
        
        return Msg(_(u'You stopped following this video now.'))
    
    def follow_language(self, language_id, user):
        if not user.is_authenticated():
            return Error(self.authentication_error_msg)
        
        try:
            language = SubtitleLanguage.objects.get(pk=language_id)
        except SubtitleLanguage.DoesNotExist:
            return Error(_(u'Subtitles does not exist.'))
        
        language.followers.add(user)
        
        return Msg(_(u'You are following this subtitles now.'))
    
    def unfollow_language(self, language_id, user):
        if not user.is_authenticated():
            return Error(self.authentication_error_msg)
        
        try:
            language = SubtitleLanguage.objects.get(pk=language_id)
        except SubtitleLanguage.DoesNotExist:
            return Error(_(u'Subtitles does not exist.'))
        
        language.followers.remove(user)
        
        return Msg(_(u'You stopped following this subtitles now.'))
    
def render_page(page, qs, on_page=VIDEOS_ON_PAGE, request=None,
                 template='videos/_watch_page.html', extra_context={},
                 display_views='total'):
    paginator = Paginator(qs, on_page)

    try:
        page = int(page)
    except ValueError:
        page = 1

    try:
        page_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'video_list': page_obj.object_list,
        'page': page_obj,
        'display_views': display_views
    }
    context.update(extra_context)

    if request:
        content = render_to_string(template, context, RequestContext(request))
    else:
        content = render_to_string(template, context)
        
    total = qs.count()
    from_value = (page - 1) * on_page + 1
    to_value = from_value + on_page - 1
    
    if to_value > total:
        to_value = total
        
    return {
        'content': content,
        'total': total,
        'pages': paginator.num_pages,
        'from': from_value,
        'to': to_value
    }
        
