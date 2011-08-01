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
import datetime
from utils.redis_utils import default_connection, RedisKey
from statistic.pre_day_statistic import BasePerDayStatistic, UpdatingLogger
from statistic.models import SubtitleFetchCounters, VideoViewCounter, WidgetViewCounter
from django.db.models import F
from django.db import models
import time

class VideoViewStatistic(BasePerDayStatistic):
    """
    statistic.WidgetViewStatistic is inherited from this. Pay attention changing 
    methods
    """
    connection = default_connection
    model = VideoViewCounter
    prefix = 'st_video_view'
    
    def get_key(self, date, video=None, video_id=None):
        if not video and not video_id:
            return
        
        video_id = video_id or video.video_id
        
        if not video_id or video_id in ['set', 'total']:
            #"set" and "total" are reserver. 
            #Don't want use more long key as prefix:keys:video_id, 
            #because video_id have more length and is generated 
            #we should never get this situation
            return 

        return '%s:%s:%s' % (self.prefix, video_id, self.date_format(date))
    
    def get_object(self, key):
        from videos.models import Video
        
        prefix, video_id, date_str = key.split(':')
        
        try:
            video = Video.objects.get(video_id=video_id)
        except Video.DoesNotExist:
            return        
        
        date = self.get_date(date_str)
        obj, created = self.model.objects.get_or_create(video=video, date=date)
        return obj

    def get_query_set(self, video):
        return self.model.objects.filter(video=video)

    def update_total(self, key, obj, value):
        video = obj.video
        video.__class__.objects.filter(pk=video.pk).update(view_count=F('view_count')+value)
        
st_video_view_handler = VideoViewStatistic()

class WidgetViewStatistic(VideoViewStatistic):
    model = WidgetViewCounter
    prefix = 'st_widget_view'
    log_to_redis = UpdatingLogger(default_connection, 'st_widget_view_migrations',
                                  u'Widget views statistic')
    
    def get_key(self, date, video=None, video_id=None):
        """
        Get get video object or video_id, to reduce DB query number in widget.rpc
        """
        if not video and not video_id:
            return
        
        video_id = video_id or video.video_id
        
        if not video_id or video_id in ['set', 'total']:
            #"set" and "total" are reserver. 
            #Don't want use more long key as prefix:keys:video_id, 
            #because video_id have more length and is generated 
            #we should never get this situation
            return 

        return '%s:%s:%s' % (self.prefix, video_id, self.date_format(date))

    def update_total(self, key, obj, value):
        from videos.models import Video
        
        Video.objects.filter(pk=obj.video_id) \
            .update(widget_views_count=F('widget_views_count')+value)
        
    def post_migrate(self, updated_objects, updated_keys):
        from utils.celery_search_index import update_search_index_for_qs
        from videos.models import Video

        def chunks(l, n):
            """ Yield successive n-sized chunks from l.
            """
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        
        for chunk in chunks(updated_objects, 200):
            print len(chunk)
            update_search_index_for_qs.delay(Video, [item.video_id for item in chunk])
            
st_widget_view_statistic = WidgetViewStatistic()

class SubtitleFetchStatistic(BasePerDayStatistic):
    connection = default_connection
    prefix = 'st_subtitles_fetch'
    model = SubtitleFetchCounters
    
    def get_key(self, date, video=None, sl=None, sl_pk=None, video_id=None):
        from videos.models import SubtitleLanguage
        
        if not video and not video_id:
            return
        
        video_id = video_id or video.video_id   
             
        if not video_id or video_id in ['set', 'total']:
            return 
        
        key = '%s:%s:' % (self.prefix, video_id)
        
        if sl_pk:
            try:
                sl = SubtitleLanguage.objects.get(pk=sl_pk)
            except (SubtitleLanguage.DoesNotExist, ValueError):
                pass
        
        if sl and sl.language:
            key += ':%s' % sl.language       
        
        key += ':%s' % self.date_format(date)
        
        return key
        
    def get_object(self, key):
        from videos.models import Video

        parts = key.split(':')
        
        if len(parts) == 6:
            lang = parts[2]
        else:
            lang = ''
        
        try:
            video = Video.objects.get(video_id=parts[1])
        except Video.DoesNotExist:
            return
        
        fields = {
            'date': self.get_date(parts[-1]),
            'video': video,
            'language': lang
        }
        obj, created = self.model.objects.get_or_create(**fields)
        return obj

    def get_query_set(self, date, video, sl=None):
        qs = self.model.objects.filter(video=video)
        
        if sl:
            qs = qs.filter(language=sl)
        
        return sl

    def update_total(self, key, obj, value):
        video = obj.video
        video.__class__.objects.filter(pk=video.pk).update(view_count=F('subtitles_fetched_count')+value)
        
st_sub_fetch_handler = SubtitleFetchStatistic()