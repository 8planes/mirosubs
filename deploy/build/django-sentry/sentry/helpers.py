import logging
import sys
import urllib
import urllib2
import uuid

import django
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.hashcompat import md5_constructor

from sentry import conf

_FILTER_CACHE = None
def get_filters():
    global _FILTER_CACHE
    
    if _FILTER_CACHE is None:
        
        filters = []
        for filter_ in conf.FILTERS:
            module_name, class_name = filter_.rsplit('.', 1)
            try:
                module = __import__(module_name, {}, {}, class_name)
                filter_ = getattr(module, class_name)
            except Exception:
                logging.exception('Unable to import %s' % (filter_,))
                continue
            filters.append(filter_)
        _FILTER_CACHE = filters
    for f in _FILTER_CACHE:
        yield f

def get_db_engine(alias='default'):
    has_multidb = django.VERSION >= (1, 2)
    if has_multidb:
        value = settings.DATABASES[alias]['ENGINE']
    else:
        assert alias == 'default', 'You cannot fetch a database engine other than the default on Django < 1.2'
        value = settings.DATABASE_ENGINE
    return value.rsplit('.', 1)[-1]

def construct_checksum(level=logging.ERROR, class_name='', traceback='', message='', **kwargs):
    checksum = md5_constructor(str(level))
    checksum.update(class_name or '')
    if traceback:
        traceback = '\n'.join(traceback.split('\n')[:-3])
    message = traceback or message
    if isinstance(message, unicode):
        message = message.encode('utf-8', 'replace')
    checksum.update(message)
    return checksum.hexdigest()

def varmap(func, var):
    if isinstance(var, dict):
        return dict((k, varmap(func, v)) for k, v in var.iteritems())
    elif isinstance(var, (list, tuple)):
        return [varmap(func, f) for f in var]
    else:
        return func(var)

def transform(value):
    # TODO: make this extendable
    # TODO: include some sane defaults, like UUID
    # TODO: dont coerce strings to unicode, leave them as strings
    if isinstance(value, (tuple, list, set, frozenset)):
        return type(value)(transform(o) for o in value)
    elif isinstance(value, uuid.UUID):
        return repr(value)
    elif isinstance(value, dict):
        return dict((k, transform(v)) for k, v in value.iteritems())
    elif isinstance(value, unicode):
        return to_unicode(value)
    elif isinstance(value, str):
        try:
            return str(value)
        except:
            return to_unicode(value)
    elif hasattr(value, '__sentry__'):
        return value.__sentry__()
    elif not isinstance(value, (int, bool)) and value is not None:
        # XXX: we could do transform(repr(value)) here
        return to_unicode(value)
    return value

def to_unicode(value):
    try:
        value = unicode(force_unicode(value))
    except (UnicodeEncodeError, UnicodeDecodeError):
        value = '(Error decoding value)'
    except Exception: # in some cases we get a different exception
        try:
            value = str(repr(type(value)))
        except Exception:
            value = '(Error decoding value)'
    return value

def get_installed_apps():
    """
    Generate a list of modules in settings.INSTALLED_APPS.
    """
    out = set()
    for app in settings.INSTALLED_APPS:
        out.add(app)
    return out

class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()

class cached_property(object):
    # This is borrowed from werkzeug : http://bytebucket.org/mitsuhiko/werkzeug-main
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. versionchanged:: 0.6
       the `writeable` attribute and parameter was deprecated.  If a
       cached property is writeable or not has to be documented now.
       For performance reasons the implementation does not honor the
       writeable setting and will always make the property writeable.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None, writeable=False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the '
                                    'cached property is a noop since 0.6 '
                                    'because the property is writeable '
                                    'by default for performance reasons'))

        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

def urlread(url, get={}, post={}, headers={}, timeout=None):
    req = urllib2.Request(url, urllib.urlencode(get), headers=headers)
    try:
        response = urllib2.urlopen(req, urllib.urlencode(post), timeout).read()
    except:
        response = urllib2.urlopen(req, urllib.urlencode(post)).read()
    return response

def get_versions(module_list=None):
    if not module_list:
        module_list = settings.INSTALLED_APPS + ['django']

    ext_module_list = set()
    for m in module_list:
        parts = m.split('.')
        ext_module_list.update('.'.join(parts[:idx]) for idx in xrange(1, len(parts)+1))

    versions = {}
    for module_name in ext_module_list:
        __import__(module_name)
        app = sys.modules[module_name]
        if hasattr(app, 'get_version'):
            get_version = app.get_version
            if callable(get_version):
                version = get_version()
            else:
                version = get_version
        elif hasattr(app, 'VERSION'):
            version = app.VERSION
        elif hasattr(app, '__version__'):
            version = app.__version__
        else:
            continue
        if isinstance(version, (list, tuple)):
            version = '.'.join(str(o) for o in version)
        versions[module_name] = version
    return versions