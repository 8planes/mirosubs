from django.utils import simplejson
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from inspect import getargspec
from Cookie import SimpleCookie
from django.utils.datastructures import MultiValueDict
from urllib import urlencode, quote
from django.utils.encoding import smart_str

class RpcMultiValueDict(MultiValueDict):
    """
    Just allow pass not list values and get only dict as argument
    """
    
    def __init__(self, key_to_list_mapping={}):
        for key, value in key_to_list_mapping.items():
            if not isinstance(value, (list, tuple)):
                key_to_list_mapping[key] = [value]
            
        super(MultiValueDict, self).__init__(key_to_list_mapping)    

    def urlencode(self, safe=None):
        output = []
        if safe:
            encode = lambda k, v: '%s=%s' % ((quote(k, safe), quote(v, safe)))
        else:
            encode = lambda k, v: urlencode({k: v})
        for k, list_ in self.lists():
            k = smart_str(k)
            output.extend([encode(k, smart_str(v))
                           for v in list_])
        return '&'.join(output)

class RpcExceptionEvent(Exception):
    """
    This exception is sent to server as Ext.Direct.ExceptionEvent.
    So we can handle it in client and show pretty message for user.
    """
    pass

class RpcResponse(dict):
    pass

class Error(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol"
    """
    def __init__(self, text, **kwargs):
        super(Error, self).__init__(error=text, **kwargs)

class Msg(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol"
    """
    def __init__(self, text, **kwargs):
        super(Msg, self).__init__(msg=text, **kwargs)

class RpcHttpResponse(RpcResponse):
    """
    This is vrapper for method's reponse, which allow save some modification of HTTP response.
    For example set COOKIES. This should be flexible and useful for in future.
    """
    
    def __init__(self, *args, **kwargs):
        super(RpcHttpResponse, self).__init__(*args, **kwargs)
        self.cookies = SimpleCookie()

    def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False):
        self.cookies[key] = value
        if max_age is not None:
            self.cookies[key]['max-age'] = max_age
        if expires is not None:
            self.cookies[key]['expires'] = expires
        if path is not None:
            self.cookies[key]['path'] = path
        if domain is not None:
            self.cookies[key]['domain'] = domain
        if secure:
            self.cookies[key]['secure'] = True

#for jQuery.Rpc
class RpcRouter(object):
    """
    Router for jQuery.Rpc calls.
    """    
    def __init__(self, url, actions={}, enable_buffer=True, max_retries=0):
        self.url = url
        self.actions = actions
        self.enable_buffer = enable_buffer
        self.max_retries = max_retries
        
    def __call__(self, request, *args, **kwargs):
        """
        This method is view that receive requests from Ext.Direct.
        """        
        user = request.user
        POST = request.POST
        
        if POST.get('extAction'):
            #Forms with upload not supported yet
            requests = {
                'action': POST.get('rpcAction'),
                'method': POST.get('rpcMethod'),
                'data': [POST],
                'upload': POST.get('rpcUpload') == 'true',
                'tid': POST.get('rpcTID')
            }
    
            if requests['upload']:
                requests['data'].append(request.FILES)
                output = simplejson.dumps(self.call_action(requests, user))
                return HttpResponse('<textarea>%s</textarea>' \
                                    % output)
        else:
            try:
                requests = simplejson.loads(request.POST.keys()[0])
            except (ValueError, KeyError, IndexError):
                requests = []
            
        if not isinstance(requests, list):
                requests = [requests]
        
        response = HttpResponse('', mimetype="application/json")
            
        output = []
        
        for rd in requests:
            mr = self.call_action(rd, request, *args, **kwargs)
            
            #This looks like a little ugly
            if 'result' in mr and isinstance(mr['result'], RpcHttpResponse):
                for key, val in mr['result'].cookies.items():
                    response.set_cookie(key, val.value, val['max-age'], val['expires'], val['path'],
                                        val['domain'], val['secure'])
                mr['result'] = dict(mr['result'])
                
            output.append(mr)
        
        response.content = simplejson.dumps(output)
            
        return response 
    
    def action_extra_kwargs(self, action, request, *args, **kwargs):
        """
        Check maybe this action get some extra arguments from request
        """  
        if hasattr(action, '_extra_kwargs'):
            return action._extra_kwargs(request, *args, **kwargs)
        return {}
    
    def method_extra_kwargs(self, method, request, *args, **kwargs):
        """
        Check maybe this method get some extra arguments from request
        """  
        if hasattr(method, '_extra_kwargs'):
            return method._extra_kwargs(request, *args, **kwargs)
        return {}
        
    def extra_kwargs(self, request, *args, **kwargs):
        """
        For all method in ALL actions we add request.user to arguments. 
        You can add something else, request for example.
        For adding extra arguments for one action use action_extra_kwargs.
        """        
        return {
            'user': request.user
        }
        
    def api(self, request, *args, **kwargs):
        """
        This method is view that send js for provider initialization.
        Just set this in template after ExtJs including:
        <script src="{% url api_url_name %}"></script>  
        """        
        obj = simplejson.dumps(self, cls=RpcRouterJSONEncoder, url_args=args, url_kwargs=kwargs)
        return HttpResponse('jQuery.Rpc.addProvider(%s)' % obj)

    def call_action(self, rd, request, *args, **kwargs):
        """
        This method checks parameters of Ext.Direct request and call method of action.
        It checks arguments number, method existing, handle RpcExceptionEvent and send
        exception event for Ext.Direct.
        """        
        method = rd['method']

        if not rd['action'] in self.actions:
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Undefined action'
            }
        
        action = self.actions[rd['action']]
        
        if not hasattr(action, method):
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Undefined method'
            }
                    
        func = getattr(action, method)
        
        args = []
        for val in (rd.get('data') or []):
            if isinstance(val, dict):
                val = RpcMultiValueDict(val)
            args.append(val)

        extra_kwargs = self.extra_kwargs(request, *args, **kwargs)
        extra_kwargs.update(self.action_extra_kwargs(action, request, *args, **kwargs))
        extra_kwargs.update(self.method_extra_kwargs(func, request, *args, **kwargs))
        
        func_args, varargs, varkw, func_defaults = getargspec(func)
        func_args.remove('self') #TODO: or cls for classmethod
        for name in extra_kwargs.keys():
            if name in func_args:
                func_args.remove(name)
        
        required_args_count = len(func_args) - len(func_defaults or [])
        if (required_args_count - len(args)) > 0 or (not varargs and len(args) > len(func_args)):
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Incorrect arguments number'
            }
        
        try:
            return {
                'tid': rd['tid'],
                'type': 'rpc',
                'action': rd['action'],
                'method': method,
                'result': func(*args, **extra_kwargs)
            }
        except RpcExceptionEvent, e:
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': unicode(e)
            }  

class RpcRouterJSONEncoder(simplejson.JSONEncoder):
    """
    JSON Encoder for RpcRouter
    """
    
    def __init__(self, url_args, url_kwargs, *args, **kwargs):
        self.url_args = url_args
        self.url_kwargs = url_kwargs
        super(RpcRouterJSONEncoder, self).__init__(*args, **kwargs)
    
    def _encode_action(self, o):
        output = []
        for method in dir(o):
            if not method.startswith('_'):
                #f = getattr(o, method)
                data = dict(name=method)
                output.append(data) 
        return output        
    
    def default(self, o):
        if isinstance(o, RpcRouter):
            output = {
                'url': reverse(o.url, args=self.url_args, kwargs=self.url_kwargs),
                'enableBuffer': o.enable_buffer,
                'actions': {},
                'maxRetries': o.max_retries
            }
            for name, action in o.actions.items():
                output['actions'][name] = self._encode_action(action)
            return output
        else:
            return super(RpcRouterJSONEncoder, self).default(o)

def add_request_to_kwargs(func):
    def extra_kwargs_func(request, *args, **kwargs):
        return dict(request=request)
    
    func._extra_kwargs = extra_kwargs_func
    return func