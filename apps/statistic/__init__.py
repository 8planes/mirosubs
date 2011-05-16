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
from statistic.pre_day_statistic import BasePerDayStatistic
from statistic.models import SubtitleFetchCounters, VideoViewCounter

widget_views_total_counter = RedisKey('StWidgetViewsTotal')
changed_video_set = RedisKey('StChangedVideos')

class VideoViewStatistic(BasePerDayStatistic):
    connection = default_connection
    model = VideoViewCounter
    prefix = 'st_video_view'
    
    def get_key(self, video, date):
        if not video.video_id or video.video_id in ['set', 'total']:
            #"set" and "total" are reserver. 
            #Don't want use more long key as prefix:keys:video_id, 
            #because video_id have more length and is generated 
            #we should never get this situation
            return 

        return '%s:%s:%s' % (self.prefix, video.video_id, self.date_format(date))
    
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

st_video_view_handler = VideoViewStatistic()
        
class SubtitleFetchStatistic(BasePerDayStatistic):
    connection = default_connection
    prefix = 'st_subtitles_fetch'
    model = SubtitleFetchCounters
    
    def get_key(self, date, video, sl=None):
        if not video.video_id or video.video_id in ['set', 'total']:
            #see VideoViewStatistic.get_key
            return 
        
        key = '%s:%s:' % (self.prefix, video.video_id)
        
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

st_sub_fetch_handler = SubtitleFetchStatistic()