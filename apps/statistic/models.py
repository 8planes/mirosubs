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
from django.db import models
from auth.models import CustomUser as User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from statistic.pre_day_statistic import BasePerDayStatisticModel

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

class BaseShareStatistic(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        abstract = True

class EmailShareStatistic(BaseShareStatistic):
    pass
    
class TweeterShareStatistic(BaseShareStatistic):
    pass

class FBShareStatistic(BaseShareStatistic):
    pass
    
class SubtitleFetchCounters(BasePerDayStatisticModel):
    video = models.ForeignKey('videos.Video')
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES, blank=True)
    
    class Meta:
        verbose_name = _(u'Subtitle fetch statistic')
        verbose_name_plural = _(u'Subtitle fetch statistic')
        unique_together = (('video', 'language', 'date'),)
        
class VideoViewCounter(BasePerDayStatisticModel):
    video = models.ForeignKey('videos.Video')
    
    class Meta:
        verbose_name = _(u'Video view statistic')
        verbose_name_plural = _(u'Video view statistic')
        unique_together = (('video', 'date'),)
        
class WidgetViewCounter(BasePerDayStatisticModel):
    video = models.ForeignKey('videos.Video')
    
    class Meta:
        verbose_name = _(u'Widget view statistic')
        verbose_name_plural = _(u'Widget view statistic')
        unique_together = (('video', 'date'),)
        
def get_model_statistics(model, today, month_ago, week_ago, day_ago):
    '''
    Gives the cronological statistics of models
    '''
    stats = {}
    stats['total'] = model.objects.count()
    stats['month'] = model.objects.filter(created__range=(month_ago, today)).count()
    stats['week'] = model.objects.filter(created__range=(week_ago, today)).count()
    stats['day'] = model.objects.filter(created__range=(day_ago, today)).count()
    return stats
