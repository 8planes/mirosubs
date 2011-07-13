try:
    import json as json
except ImportError:    
    import simplejson as json
import time
import datetime

from django.db import models
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings
from django.utils.functional import Promise, wraps
from django.utils.encoding import force_unicode
from django.http import HttpResponse
import logging

class LazyEncoder(DateTimeAwareJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise) :
            return force_unicode(obj)
        elif isinstance(obj, datetime.datetime):
            return time.strftime("%d-%m-%Y %H-%M-%S")
        elif isinstance(obj, models.query.ValuesQuerySet):
            return self.default(list(obj))
        try:
            return super(LazyEncoder, self).default(obj)
        except:
            raise

def _json_response(data, response=None):
    """
    Simple wrapper that encodes response to json and sets the
    correct content-type.
    """
    final_data = {}
    suc = False
    errors = None
    if isinstance(data, dict):
        suc =  data.pop('success', False)
        errors = data.pop('errors', None)
    if errors is not None:
        final_data['errors'] = errors
        suc = False
    if  errors is None: 
        suc = True
        final_data['data']= data
    final_data['success'] = suc
    
    response = response or HttpResponse()
    response['Content-Type'] = "application/json; charset=UTF-8"
    json_res = json.dumps(final_data,cls=LazyEncoder, ensure_ascii=True)
    response.write( json_res)
    return response

def _json_errors(errors):
        return _json_response({'success':False, 'errors':errors})

def to_json(view):
    def wrapper(request, *args, **kwargs):
        try:
            res = view(request, *args, **kwargs)
            response = None
            if isinstance(res, HttpResponse):
                res = res.content
            return _json_response(res, response)
        except:
            logging.exception("Error on view %s" % view.__name__)
            if settings.DEBUG:
                raise
            return _json_errors("Something is wrong")
    return wraps(view)(wrapper)

def post_required(view):
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return {'errors':['POST REQUIRED']}
        return view(request, *args, **kwargs)
    return wraps(view)(wrapper)
