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
from utils import render_to, render_to_json
from datetime import datetime, timedelta
from videos.models import Video, SubtitleLanguage, ALL_LANGUAGES
from statistic.models import EmailShareStatistic, TweeterShareStatistic, FBShareStatistic, SubtitleFetchStatistic
from auth.models import CustomUser as User
from django.views.generic.list_detail import object_list
from comments.models import Comment
from django.db.models import Sum, Count
from django.http import Http404
from django.views.decorators.cache import cache_page

@cache_page(60 * 60 * 24)
@render_to('statistic/index.html')
def index(request):
    today = datetime.today()
    month_ago = today - timedelta(days=31)
    week_ago = today - timedelta(weeks=1)
    day_ago = today - timedelta(days=1)
    
    videos_st = {}
    videos_st['total'] = Video.objects.count()
    videos_st['month'] = Video.objects.filter(created__range=(month_ago, today)).count()
    videos_st['week'] = Video.objects.filter(created__range=(week_ago, today)).count()
    videos_st['day'] = Video.objects.filter(created__range=(day_ago, today)).count()

    tweet_st = {}
    tweet_st['total'] = TweeterShareStatistic.objects.count()
    tweet_st['month'] = TweeterShareStatistic.objects.filter(created__range=(month_ago, today)).count()
    tweet_st['week'] = TweeterShareStatistic.objects.filter(created__range=(week_ago, today)).count()
    tweet_st['day'] = TweeterShareStatistic.objects.filter(created__range=(day_ago, today)).count()
    
    fb_st = {}
    fb_st['total'] = FBShareStatistic.objects.count()
    fb_st['month'] = FBShareStatistic.objects.filter(created__range=(month_ago, today)).count()
    fb_st['week'] = FBShareStatistic.objects.filter(created__range=(week_ago, today)).count()
    fb_st['day'] = FBShareStatistic.objects.filter(created__range=(day_ago, today)).count()
    
    email_st = {}
    email_st['total'] = EmailShareStatistic.objects.count()
    email_st['month'] = EmailShareStatistic.objects.filter(created__range=(month_ago, today)).count()
    email_st['week'] = EmailShareStatistic.objects.filter(created__range=(week_ago, today)).count()
    email_st['day'] = EmailShareStatistic.objects.filter(created__range=(day_ago, today)).count()

    context = {
        'subtitles_fetched_count': Video.objects.aggregate(c=Sum('subtitles_fetched_count'))['c'],
        'view_count': Video.objects.aggregate(c=Sum('view_count'))['c'],
        'videos_with_captions': Video.objects.exclude(subtitlelanguage=None).count(),
        'all_videos': Video.objects.count(),
        'all_users': User.objects.count(),
        'translations_count': SubtitleLanguage.objects.filter(is_original=False).count(),
        'fineshed_translations': SubtitleLanguage.objects.filter(is_original=False, was_complete=True).count(),
        'unfineshed_translations': SubtitleLanguage.objects.filter(is_original=False, was_complete=False).count(),
        'all_comments': Comment.objects.count(),
        'videos_st': videos_st,
        'tweet_st': tweet_st,
        'fb_st': fb_st,
        'email_st': email_st        
    }
           
    return context

@cache_page(60 * 60 * 24)
@render_to_json    
def update_share_statistic(request, cls):
    st = cls()
    if request.user.is_authenticated():
        st.user = request.user
    st.save()
    return {}

@cache_page(60 * 60 * 24)
@render_to('statistic/languages_statistic.html')
def languages_statistic(request):
    today = datetime.today()
    month_ago = today - timedelta(days=31)
    week_ago = today - timedelta(weeks=1)
    day_ago = today - timedelta(days=1)

    total_langs = SubtitleLanguage.objects.values('language').annotate(lc=Count('language'))
    month_langs = SubtitleLanguage.objects.filter(created__range=(month_ago, today)).values('language').annotate(lc=Count('language'))
    week_langs = SubtitleLanguage.objects.filter(created__range=(week_ago, today)).values('language').annotate(lc=Count('language'))
    day_langs = SubtitleLanguage.objects.filter(created__range=(day_ago, today)).values('language').annotate(lc=Count('language'))
    
    lang_names = dict(ALL_LANGUAGES)
    lang_names[u''] = 'No name'
    langs = dict((i['language'], {'name': lang_names[i['language']], 'total': i['lc'], 'month': 0, 'week': 0, 'day': 0}) for i in total_langs)
    for item in month_langs:
        langs[item['language']]['month'] = item['lc']
    for item in week_langs:
        langs[item['language']]['week'] = item['lc']
    for item in day_langs:
        langs[item['language']]['day'] = item['lc']
                        
    return {
        'langs': langs
    }

@cache_page(60 * 60 * 24)
@render_to('statistic/language_statistic.html')
def language_statistic(request, lang):
    lang_names = dict(ALL_LANGUAGES)
    lang_names[u''] = 'No name'
            
    if lang == 'undefined':
        lang = u''
        
    if not lang in lang_names:
        raise Http404
            
    today = datetime.today()
    month_ago = today - timedelta(days=31)
    week_ago = today - timedelta(weeks=1)
    day_ago = today - timedelta(days=1)
    
    videos_count = {}
    videos_count['total'] = SubtitleLanguage.objects.filter(language=lang).count()
    videos_count['month'] = SubtitleLanguage.objects.filter(created__range=(month_ago, today)).filter(language=lang).count()
    videos_count['week'] = SubtitleLanguage.objects.filter(created__range=(week_ago, today)).filter(language=lang).count()
    videos_count['day'] = SubtitleLanguage.objects.filter(created__range=(day_ago, today)).filter(language=lang).count()
    
    subtitles_view_count = {}
    subtitles_view_count['total'] = SubtitleLanguage.objects.filter(language=lang) \
        .aggregate(Sum('subtitles_fetched_count'))['subtitles_fetched_count__sum']
    subtitles_view_count['month'] = SubtitleFetchStatistic.objects.filter(language=lang) \
        .filter(created__range=(month_ago, today)).count()
    subtitles_view_count['week'] = SubtitleFetchStatistic.objects.filter(language=lang) \
        .filter(created__range=(week_ago, today)).count()    
    subtitles_view_count['day'] = SubtitleFetchStatistic.objects.filter(language=lang) \
        .filter(created__range=(day_ago, today)).count()
    
    videos_views_count = Video.objects.filter(subtitlelanguage__language=lang) \
        .aggregate(Sum('widget_views_count'))['widget_views_count__sum']
            
    return {
        'video_count': videos_count,
        'lang_name': lang_names[lang],
        'subtitles_view_count': subtitles_view_count,
        'videos_views_count': videos_views_count
    }

@cache_page(60 * 60 * 24)
def videos_statistic(request):
    today = datetime.today()
    month_ago = today - timedelta(days=31)
    week_ago = today - timedelta(weeks=1)
    day_ago = today - timedelta(days=1)
    
    tn = 'statistic_subtitlefetchstatistic'
        
    qs = Video.objects.distinct().extra(select={
        'month_activity': ('SELECT COUNT(id) FROM %s WHERE %s.video_id = videos_video.id '+
        'AND %s.created BETWEEN "%s" and "%s"') % (tn, tn, tn, month_ago, today),                                          
        'week_activity': ('SELECT COUNT(id) FROM %s WHERE %s.video_id = videos_video.id '+
        'AND %s.created BETWEEN "%s" and "%s"') % (tn, tn, tn, week_ago, today),
        'day_activity': ('SELECT COUNT(id) FROM %s WHERE %s.video_id = videos_video.id '+
        'AND %s.created BETWEEN "%s" and "%s"') % (tn, tn, tn, day_ago, today)
    })

    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    
    extra_context = {}
    order_fields = ['title', 'subtitles_fetched_count', 'month_activity', 'week_activity', 'day_activity']
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+ordering)
        extra_context['ordering'] = ordering
        extra_context['order_type'] = order_type
    else:
        qs = qs.order_by('-subtitles_fetched_count') 
              
    return object_list(request, queryset=qs,
                       paginate_by=30,
                       template_name='statistic/videos_statistic.html',
                       template_object_name='video',
                       extra_context=extra_context)

@cache_page(60 * 60 * 24)
def users_statistic(request):
    today = datetime.today()
    month_ago = today - timedelta(days=31)
    week_ago = today - timedelta(weeks=1)
    day_ago = today - timedelta(days=1)
        
    qs = User.objects.distinct().extra(select={
        'total_activity': 'SELECT COUNT(id) FROM videos_action WHERE videos_action.user_id = auth_user.id',                                          
        'month_activity': 'SELECT COUNT(id) FROM videos_action WHERE videos_action.user_id = auth_user.id '+
        'AND videos_action.created BETWEEN "%s" and "%s"' % (month_ago, today),                                          
        'week_activity': 'SELECT COUNT(id) FROM videos_action WHERE videos_action.user_id = auth_user.id '+
        'AND videos_action.created BETWEEN "%s" and "%s"' % (week_ago, today),
        'day_activity': 'SELECT COUNT(id) FROM videos_action WHERE videos_action.user_id = auth_user.id '+
        'AND videos_action.created BETWEEN "%s" and "%s"' % (day_ago, today)
    })

    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    
    extra_context = {}
    order_fields = ['username', 'total_activity', 'month_activity', 'week_activity', 'day_activity']
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+ordering)
        extra_context['ordering'] = ordering
        extra_context['order_type'] = order_type
    else:
        qs = qs.order_by('-total_activity')    
    return object_list(request, queryset=qs,
                       paginate_by=30,
                       template_name='statistic/users_statistic.html',
                       template_object_name='user',
                       extra_context=extra_context)