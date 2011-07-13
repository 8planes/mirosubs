from django.conf import settings
from django.http import HttpResponse, Http404
from django.db.models.base import ObjectDoesNotExist
from django.utils.translation import ugettext as _
import json


class AjaxErrorMiddleware(object):
    '''Return AJAX errors to the browser in a sensible way.

    Includes some code from http://www.djangosnippets.org/snippets/650/
    '''

    # Some useful errors that this middleware will catch.
    class InputError(Exception):
        def __init__(self, message):
            self.message = message

    class ParameterMissingError(InputError):
        def __init__(self, param):
            super(AjaxErrorMiddleware.ParameterMissingError, self).__init__(
                _('Required parameter missing: %s') % param)


    def process_exception(self, request, exception):
        if not request.is_ajax(): return

        if isinstance(exception, (ObjectDoesNotExist, Http404)):
            return self.not_found(request, exception)

        if isinstance(exception, AjaxErrorMiddleware.InputError):
            return self.bad_request(request, exception)

        return self.server_error(request, exception)
    

    def serialize_error(self, status, message):
        return HttpResponse(json.dumps({
                    'status': status,
                    'message': message}),
                            status=status)

    
    def not_found(self, request, exception):
        return self.serialize_error(404, str(exception))

    
    def bad_request(self, request, exception):
        return self.serialize_error(400, exception.message)


    def server_error(self, request, exception):
        if settings.DEBUG:
            import sys, traceback
            (exc_type, exc_info, tb) = sys.exc_info()
            message = "%s\n" % exc_type.__name__
            message += "%s\n\n" % exc_info
            message += "TRACEBACK:\n"    
            for tb in traceback.format_tb(tb):
                message += "%s\n" % tb
            return self.serialize_error(500, message)
        else:
            return self.serialize_error(500, _('Internal error'))
