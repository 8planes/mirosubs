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
from django.contrib.admin import ModelAdmin
from django.views.generic.simple import direct_to_template
from django.core.paginator import EmptyPage, InvalidPage, Paginator
import datetime
import time
from django.views.generic.list_detail import object_list

class LoggerModelAdmin(ModelAdmin):
    logger = None
    verbose_name = u'Redis->MySql migration statistic'
    verbose_name_plural = u'Redis->MySql migration statistic'
    
    @classmethod
    def model(cls):
        class LoggerFakeModel(models.Model):
            
            class Meta:
                managed = False
                verbose_name = cls.verbose_name
                verbose_name_plural = cls.verbose_name_plural
        
        return LoggerFakeModel
    
    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label
        title = opts.verbose_name_plural

        context = {
            'app_label': app_label,
            'title': title
        }
        return object_list(request, queryset=self.logger,
                           paginate_by=self.list_per_page,
                           template_name='statistic/logger_model_admin.html',
                           template_object_name='object',
                           extra_context=context)        
    
    def has_change_permission(self, request, obj=None):
        return not bool(obj)
            
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

class UpdatingLogger(object):
    date_format = '%Y.%m.%d..%H.%M.%S' 
    
    def __init__(self, connection, prefix, name):
        self.conn = connection
        self.prefix = prefix
        self.name = name
        self.id_key = RedisKey('%s:id' % self.prefix, self.conn)
        self.set_key = RedisKey('%s:set' % self.prefix, self.conn)
        
    def save(self, date, value, t):
        id = self.id_key.incr()
        key = '%s:obj:%s' % (self.prefix, id)
        date_str = date.strftime(self.date_format)
        self.conn.hmset(key, {'value': value, 'date': date_str, 'time': t})
        self.set_key.sadd(id)

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, slice):
            raise TypeError
        
        num = k.stop - k.start
        key = self.set_key.redis_key
        p = self.prefix
        get = ['%s:obj:*->value' % p, '%s:obj:*->date' % p, '%s:obj:*->time' % p]
        return self._to_python(self.conn.sort(key, get=get, start=k.start, num=num, desc=True))
    
    def count(self):
        return self.set_key.scard()
    
    def _get_date(self, value):
        return datetime.datetime.strptime(value, self.date_format)
    
    def _clone(self):
        return self
    
    def _to_python(self, result):
        output = []
        
        for i in range(len(result))[::3]:
            obj = {}
            obj['value'] = result[i]
            obj['date'] = self._get_date(result[i+1])
            obj['time'] = result[i+2]
            output.append(obj)
            
        return output
        
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
    Base of handler for saving per-day statistic in Redis and migration it to DB.
    For using create subclass and implement *get_key*, *get_object*, *get_query_set*
    methods and *connection*, *prefix*, *model* attributes.
    
    Then create instance and use *update* method with kwargs you need in *get_key*
    method to make unique key for Redis counter.
    For migration use *instance.migrate()* method.
    To get views statistic use *get_views* methods with kwargs to find static
    in database. These kwargs will be passed to *get_query_set* method.
    
    For example, you wish save some view statistic for *Video* object. 
    *BasePerDayStatisticModel* subclass model should have FK to *Video* model.
    Pass *Video* instance to *update* method to update statistic for this video.
    
    Then in *get_key* you get *video* and *date* arguments, where *video* is
    instance you pass to *update* method and *date* is current date. Your *get_key*
    method should return Redis key to update counter. Don't forget about *prefix*
    to prevent collisions.
    Example:
    
        def get_key(self, video, date):
            return '%s:%s:%s' % (self.prefix, video.pk, self.date_format(date))
            
    When *migrate* method is executed, each saved Redis key is checked and
    information is moved to DB. It is saved in *model*. You should implement
    *get_object* method witch should return *model* instance from Redis key 
    to save statistic.
    For example:
    
        def get_object(self, key):
            prefix, pk, date_str = key.split(':')
            date = self.get_date(date_str)
            obj, created = self.model.objects.get_or_create(video_id=pk, date=date)
            return obj
            
    The last method you should implement is *get_query_set*. This method make
    base filtration for QuerySet to get views statistic, because really only you
    know how statistic model is related to some objects. This method get everything
    you pass to *get_views* methods. So if you are using *get_views(video)* this
    can looks like:
    
        def get_query_set(self, video):
            return self.model.objects.filter(video=video)
    
    Really *get_query_set* and *get_key* should get same arguments, because 
    as you update statistic for some objects, for same you wish get this statistic
    in future.
    """
    connection = None   #Redis connection
    prefix = None       #keys' prefix
    model = None        #Model to save info in DB, BasePerDayStatisticModel subclass
    log_to_redis = None
    
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
        """
        Generate part of Redis key to save *date*
        """
        return '%s-%s-%s' % (date.year, date.month, date.day)
    
    def get_date(self, s):
        """
        Return date from part of Redis key witch was generated by *date_format*
        method
        """
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
    
    def update_total(self, key, obj, value):
        """
        Should update total counter for one instance. 
        key - Redis key, the same that is passed to *get_object*
        obj - object returned by *get_object*. This is NOT object that was viewed
        value - number of views
        
        Example:
        
        def update_total(self, key, obj, value):
            video = obj.video
            video.__class__.objects.filter(pk=video.pk).update(view_count=F('view_count')+value)        
        """
        raise Exception('Not implemented')
        
    def get_views(self, **kwargs):
        """
        Return views statistic for week and month like: {'month': value, 'week': value, 'year': value}
        Pas
        """
        qs = self.get_query_set(**kwargs)
        today = datetime.datetime.today()
        yesterday  = today - datetime.timedelta(days=1)
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)
        year_ago = today - datetime.timedelta(days=365)
        
        #TODO: refactor this. too many queries. 
        result = dict(week=0, month=0)
        result['week'] = qs.filter(date__range=(week_ago, today)) \
            .aggregate(s=models.Sum('count'))['s'] or 0
        result['month'] = qs.filter(date__range=(month_ago, today)) \
            .aggregate(s=models.Sum('count'))['s'] or 0
        result['year'] = qs.filter(date__range=(year_ago, today)) \
            .aggregate(s=models.Sum('count'))['s'] or 0

        today_views = qs.filter(date=today).aggregate(s=models.Sum('count'))['s'] or 0
        yesterday_views = qs.filter(date=yesterday).aggregate(s=models.Sum('count'))['s'] or 0
        result['today'] =  int(today_views + yesterday_views * (1 - today.hour / 24.))
                    
        return result
    
    def post_migrate(self, updated_objects, updated_keys):
        """
        This method is executed after migration to DB
        """
        pass

    def pre_migrate(self):
        """
        This method is executed after migration to DB
        """
        pass
    
    def migrate(self, verbosity=1):
        """
        Migrate information from Redis to DB
        """
        start = time.time()
        
        self.pre_migrate()
        
        count = self.set_key.scard()
        
        i = count 
        
        updated_keys = []
        updated_objects = []
        
        while i:
            if verbosity >= 2 and (count - i) % 100 == 0:
                print '  >>> migrate key: %s of %s' % ((count - i), count)
                 
            i -= 1
            key = self.set_key.spop()
            if not key:
                break
            
            updated_keys.append(key)
            
            obj = self.get_object(key)
            if obj:
                try:
                    value = int(self.connection.getset(key, 0))
                    
                    obj.__class__._default_manager.filter(pk=obj.pk) \
                        .update(count=models.F('count')+value)

                    self.update_total(key, obj, value)

                    updated_objects.append(obj)
                except (TypeError, ValueError):
                    pass
                self.connection.delete(key)

        self.post_migrate(updated_objects, updated_keys)

        if self.log_to_redis and count:
            self.log_to_redis.save(datetime.datetime.now(), count, time.time()-start)

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