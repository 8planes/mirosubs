import logging
import inspect
from utils.redis_utils import RedisKey
from django.contrib.sites.models import Site
from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.views.generic.simple import direct_to_template
from django import db

"""
Admin interface
"""
class LogFakeModel(models.Model):
    
    class Meta:
        managed = False
        verbose_name = u'API usage statistic'
        verbose_name_plural = u'API usage statistic'
        
class LogAdmin(ModelAdmin):
    _registery = {}
    
    @classmethod
    def register(cls, logger_name, logger):
        if logger.saves_data and logger_name not in cls._registery:
            cls._registery[logger_name] = logger
    
    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label
        title = opts.verbose_name_plural
        
        selected_logger = request.GET.get('logger')
        
        if selected_logger and selected_logger in self._registery:
            registery = {}
            registery[selected_logger] = self._registery[selected_logger]
        else:
            registery = self._registery
            selected_logger = None
        
        filter_choices = self._registery.keys()
        
        context = {
            'app_label': app_label,
            'registery': registery,
            'selected_logger': selected_logger,
            'filter_choices': filter_choices,
            'title': title
        }
        return direct_to_template(request, 'statistic/log_methods/changelist_view.html', context)
    
    def has_change_permission(self, request, obj=None):
        return not bool(obj)
            
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
"""
Backends
"""
class BaseLogBackend(object):
    saves_data = True #can save and show collected data
        
    def log(self, logger, event_name, *args, **kwargs):
        raise Exception('Should be implemented')

class ConsoleLogBackend(BaseLogBackend):
    saves_data = False
    
    def log(self, logger, event_name, *args, **kwargs):
        print 'Event logger: ', logger, event_name

class RedisLogBackend(BaseLogBackend):
    
    def __init__(self, connection, prefix='event_logger'):
        self.conn = connection
        self.prefix = prefix
        self.site_name = Site.objects.get_current().name.replace(':', '')
        
        #Site.objects.get_current() created new DB connection
        #RedisLogBackend.__init__ is executed when you add it to class
        #so, for example, celery worker process will have opened DB connection
        #that cause bugs
        db.connection.close()
        
        #keys cache
        self.keys = {}
        self.key_set = self._get_key('logger_keys')

    def _get_key(self, key):
        if not key in self.keys:
            self.keys[key] = RedisKey('%s:%s:%s' % (self.site_name, self.prefix, key), self.conn)
        
        return self.keys[key]

    def log(self, logger, event_name, *args, **kwargs):
        key = self._get_key('events:%s:%s' % (logger, event_name))
        self.key_set.sadd(key.redis_key)
        key.incr()
    
    def list(self):
        for key in self.key_set.smembers():
            obj = {}
            key_parts = key.split(':')
            obj['cls'], obj['method'] = key_parts[3], key_parts[4]
            obj['value'] = RedisKey(key).val
            yield obj
    
"""
Classes for adding logging
"""
class LogNativeMethodsMetaclass(type):
    
    @classmethod
    def wrap(cls, func, name, logger_backend):
        def wrapper(*args, **kwargs):
            val = func(*args, **kwargs)
            logger_backend.log(name, func.__name__, args, kwargs)
            return val
        
        #from django.utils.functional.update_wrapper. Don't want have dependency
        for attr in ('__module__', '__name__', '__doc__'):
            setattr(wrapper, attr, getattr(func, attr))
        for attr in ('__dict__',):
            getattr(wrapper, attr).update(getattr(func, attr))
            
        return wrapper
    
    def __new__(cls, name, bases, attrs):
        logger_backend = attrs.get('logger_backend', ConsoleLogBackend())
        
        attrs['logger_backend'] = logger_backend

        for n, v in attrs.items():
            if inspect.isfunction(v):
                attrs[n] = cls.wrap(v, name, logger_backend)
        
        for base in bases:
            for n, v in inspect.getmembers(base):
                if not n in attrs and inspect.ismethod(v):
                    attrs[n] = cls.wrap(v, name, logger_backend)
        new_class = super(LogNativeMethodsMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class