import logging
import inspect
from utils.redis_utils import RedisKey
from django.contrib.sites.models import Site

class BaseLogBackend(object):
    
    def log(self, logger, event_name, *args, **kwargs):
        raise Exception('Should be implemented')

class ConsoleLogBackend(BaseLogBackend):

    def log(self, logger, event_name, *args, **kwargs):
        print 'Event logger: ', logger, event_name

class RedisLogBackend(BaseLogBackend):
    
    def __init__(self, connection, prefix='event_logger'):
        self.conn = connection
        self.prefix = prefix
        self.site_name = Site.objects.get_current().name.replace(':', '')
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
        print '__new__', cls, name
        
        logger_backend = attrs.get('logger_backend', ConsoleLogBackend())
        
        if 'logger_backend' in attrs:
            del attrs['logger_backend']
        
        for base in bases:
            for n, v in base.__dict__.items():
                if inspect.isfunction(v):
                    attrs[n] = cls.wrap(v, name, logger_backend)
        new_class = super(LogNativeMethodsMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class
