from redis import Redis
from django.conf import settings
from utils import catch_exception
from redis.exceptions import RedisError
from inspect import ismethod
from django.utils.functional import update_wrapper

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 0)
IGNORE_REDIS = getattr(settings, 'IGNORE_REDIS', False) and settings.DEBUG

default_connection = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

catch_exception_dec = catch_exception(RedisError, u'Redis error', '', ignore=True)

class RedisCounterField(Exception):
    pass

class RedisCounterFieldNotUnique(RedisCounterField):
    pass

class RedisCounterFieldNoSettings(RedisCounterField):
    pass

def redis_key_wrapper(func, key):
    def wrapper(*args, **kwargs):
        if IGNORE_REDIS:
            return
        return func(key, *args, **kwargs)
    return update_wrapper(wrapper, func)

class RedisKey(object):

    def __init__(self, key, r=None):
        self.redis_key = key
        self.r = r or default_connection

    def __repr__(self):
        return "<%s>: %s -> %s" % (self.__class__.__name__, self.redis_key, self.val)

    def __str__(self):
        return "%s -> %s" % (self.redis_key, self.val)
    
    def __getattr__(self, name):     
        if hasattr(self.r, name):
            method = getattr(self.r, name)
            if ismethod(method):
                return catch_exception_dec(redis_key_wrapper(method, self.redis_key))
        raise AttributeError
    
    @catch_exception_dec
    def set_val(self, val):
        if IGNORE_REDIS:
            return
        #get rid from this: user get, set
        return self.r.set(self.redis_key, val)

    @catch_exception_dec
    def get_val(self):
        if IGNORE_REDIS:
            return        
        return self.r.get(self.redis_key)

    val = property(get_val, set_val)

class RedisSimpleField(object):
    """
    Redis incremental field
    """
    def __init__(self, uniq_attr=None, changed_set=None):
        self.uniq_attr = uniq_attr
        self.r = default_connection
        self.changed_set = changed_set
        # use object method for generating unique id
        #if uniq_attr and hasattr(self.obj, self.uniq_attr):
        #    self.instance_id = getattr(self.obj, self.uniq_attr)
        # django helper if no special method for generating unique id
        #elif hasattr(self.obj, '_meta') and self.obj._meta.has_auto_field:
        #    self.instance_id = u"%s:%s" % (self.obj._meta.auto_field.name, self.obj.pk)
        #else:
        #    raise RedisCounterFieldNotUnique
        # generate unique redis key for object
        #self.redis_key = u"%s:%s:%s" % (self.class_name, self.field_name, self.instance_id)
        # setup redis connection credentials
        

    def contribute_to_class(self, cls, name):
        self.field_name = name
        self.class_name = cls.__name__
        setattr(cls, self.field_name, self)

    def redis_key(self, obj):
        if self.uniq_attr and hasattr(obj, self.uniq_attr):
            instance_id = getattr(obj, self.uniq_attr)
        else:
            instance_id = obj.pk
        self.add_to_changed_set(instance_id)
        return u"%s:%s:%s" % (self.class_name, self.field_name, instance_id)
    
    def add_to_changed_set(self, instance_id):
        if self.changed_set:
            self.changed_set.sadd(instance_id)
        
    def __set__(self, obj, val):
        RedisKey(self.redis_key(obj), self.r).val = val

    def __get__(self, obj, cls=None):
        if not obj:
            return self
        return RedisKey(self.redis_key(obj), self.r)

    def __call__(self, instance_id, skip_mark_as_changed=False):
        if not skip_mark_as_changed:
            self.add_to_changed_set(instance_id)
        key = u"%s:%s:%s" % (self.class_name, self.field_name, instance_id)
        return RedisKey(key, self.r)
