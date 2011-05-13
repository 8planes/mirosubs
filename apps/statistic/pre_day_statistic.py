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
from utils.redis_utils import RedisKey
import datetime

class BasePerDayStatisticModel(models.Model):
    """
    Base Model for saving statistic information in DB
    """
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
    
class BasePerDayStatistic(object):
    """
    Base of handler for saving per-day statistic in Redis and migration it to DB
    """
    connection = None   #Redis connection
    prefix = None       #keys' prefix
    model = None        #Model to save info in DB
    
    def __init__(self):
        if not self.connection:
            raise Exception('Connection undefined')
        
        if not self.prefix:
            raise Exception('Prefix undefined')
        
        if not issubclass(self.model, BasePerDayStatisticModel):
            raise Exception('Model should subclass of BasePerDayStatisticModel')
        
        self.total_key = self._create_total_key()
        self.set_key = self._create_set_key()
    
    def _create_set_key(self):
        return RedisKey('%s:set' % self.prefix, self.connection)
    
    def _create_total_key(self):
        return RedisKey('%s:total' % self.prefix, self.connection)
    
    def date_format(self, date):
        return '%s-%s-%s' % (date.year, date.month, date.day)
    
    def get_date(self, s):
        return datetime.date(*map(int, s.split('-')))       
    
    def get_key(self, date, **kwargs):
        """
        Method should return Redis key for date and arguments passed to update method
        User this format: PREFIX:keys:... 
        or pay attentions that PREFIX:set and PREFIX:total are reserved
        Return None if you wish not save this data
        """
        raise Exception('Not implemented')
    
    def get_object(self, key):
        """
        Method should return instance of self.model for saving statistic in DB
        User self.model. Return None if don't want save this data
        """
        raise Exception('Not implemented')        
    
    def get_query_set(self, **kwargs):
        """
        Should return QuerySet for self.model for get_views method
        """
        raise Exception('Not implemented')
        
    def get_views(self, **kwargs):
        """
        Return views statistic for week and month
        """
        qs = self.get_query_set(**kwargs)
    
    def migrate(self, verbosity=1):
        """
        Migrate information from Redis to DB
        """
        count = self.set_key.scard()
        
        i = count 
        
        while i:
            if verbosity >= 1:
                print '  >>> migrate key: ', i
                 
            i -= 1
            key = self.set_key.spop()
            if not key:
                break
            
            obj = self.get_object(key)
            if obj:
                obj.count += int(self.connection.getset(key, 0))
                obj.save()
                self.connection.delete(key)
        
        return count
        
    def update(self, **kwargs):
        """
        Update counter for date in Redis
        """
        date = kwargs.get('date', datetime.date.today())
        key = self.get_key(date=date, **kwargs)
        
        if not key:
            return
        
        self.connection.incr(key)
        self.set_key.sadd(key)
        self.total_key.incr()    