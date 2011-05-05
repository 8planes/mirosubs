import logging
import inspect
    
class LogNativeMethodsMetaclass(type):
    
    @staticmethod
    def log(func, args, kwargs):
        logging.debug(func.__name__, args, kwargs)
        
    @classmethod
    def wrap(cls, func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            val = func(*args, **kwargs)
            cls.log(func, args, kwargs)
            return val
        
        #from django.utils.functional.update_wrapper. Don't want have dependency
        for attr in ('__module__', '__name__', '__doc__'):
            setattr(wrapper, attr, getattr(func, attr))
        for attr in ('__dict__',):
            getattr(wrapper, attr).update(getattr(func, attr))
            
        return wrapper
    
    def __new__(cls, name, bases, attrs):
        for base in bases:
            for n, v in base.__dict__.items():
                if inspect.isfunction(v):
                    attrs[n] = cls.wrap(v)
        new_class = super(LogNativeMethodsMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class    