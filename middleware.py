import time

from django.conf import settings
import random
from django.utils.hashcompat import sha_constructor
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
import os
from django.db import connection
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

class SaveUserIp(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            ip = request.META.get('REMOTE_ADDR', '')
            try:
                validate_ipv4_address(ip)
                if request.user.last_ip != ip:
                    request.user.last_ip = ip
                    request.user.save()
            except ValidationError:
                pass
        
class P3PHeaderMiddleware(object):
    def process_response(self, request, response):
        response['P3P'] = settings.P3P_COMPACT
        return response


# Got this from CsrfViewMiddleware
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
    
_MAX_CSRF_KEY = 18446744073709551616L     # 2 << 63

UUID_COOKIE_NAME = getattr(settings, 'UUID_COOKIE_NAME', 'unisub-user-uuid')
UUID_COOKIE_DOMAIN = getattr(settings, 'UUID_COOKIE_DOMAIN', None)

def _get_new_csrf_key():
    return sha_constructor("%s%s"
                % (randrange(0, _MAX_CSRF_KEY), settings.SECRET_KEY)).hexdigest()

class UserUUIDMiddleware(object):
    
    def process_request(self, request):
        try:
            request.browser_id = request.COOKIES[UUID_COOKIE_NAME]
        except KeyError:
            # No cookie or it is empty, so create one.  This will be sent with the next
            # response.            
            if not hasattr(request, 'browser_id'):
                request.browser_id = _get_new_csrf_key()

    def process_response(self, request, response):
        if hasattr(request, 'browser_id'):
            browser_id = request.browser_id
            if request.COOKIES.get(UUID_COOKIE_NAME) != browser_id:
                max_age = 60 * 60 * 24 * 365
                response.set_cookie(
                    UUID_COOKIE_NAME,
                    browser_id, 
                    max_age=max_age,
                    expires=cookie_date(time.time() + max_age),
                    domain=UUID_COOKIE_DOMAIN)
        # Content varies with the CSRF cookie, so set the Vary header.
        patch_vary_headers(response, ('Cookie',))
        return response            

def _terminal_width():
    """
    Function to compute the terminal width.
    WARNING: This is not my code, but I've been using it forever and
    I don't remember where it came from.
    """
    width = 0
    try:
        import struct, fcntl, termios
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack('HHHH', x)[1]
    except:
        pass
    if width <= 0:
        try:
            width = int(os.environ['COLUMNS'])
        except:
            pass
    if width <= 0:
        width = 80
    return width

DISABLE_SQL_PRINTING = getattr(settings, 'DISABLE_SQL_PRINTING', False)

class SqlPrintingMiddleware(object):
    """
    Middleware which prints out a list of all SQL queries done
    for each view that is processed.  This is only useful for debugging.
    """
    def process_response(self, request, response):
        indentation = 2
        if len(connection.queries) > 0 and settings.DEBUG and not DISABLE_SQL_PRINTING:
            width = _terminal_width()
            total_time = 0.0
            for query in connection.queries:
                nice_sql = query['sql'].replace('"', '').replace(',',', ')
                sql = "\033[1;31m[%s]\033[0m %s" % (query['time'], nice_sql)
                total_time = total_time + float(query['time'])
                while len(sql) > width-indentation:
                    print "%s%s" % (" "*indentation, sql[:width-indentation])
                    sql = sql[width-indentation:]
                print "%s%s\n" % (" "*indentation, sql)
            replace_tuple = (" "*indentation, str(total_time))
            print "%s\033[1;32m[TOTAL TIME: %s seconds]\033[0m" % replace_tuple
        return response

from debug_toolbar.middleware import DebugToolbarMiddleware
import debug_toolbar

class SupeuserDebugToolbarMiddleware(DebugToolbarMiddleware):
    
    def _show_toolbar(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0].strip()
        else:
            remote_addr = request.META.get('REMOTE_ADDR', None)
        if (not remote_addr in settings.INTERNAL_IPS and not request.user.is_superuser) \
            or (request.is_ajax() and \
                not debug_toolbar.urls._PREFIX in request.path) \
                    or not settings.DEBUG:
            return False
        return True

class InjectEnviron(object):

    """
    Sets a "ENV_IS_PRODUCTION" bool the request. This can be used in views and
    templates as a way to make sure which environment wer are running at.
    """
    def process_request(self, request):
        request.MIDDLE_YES = "arthur"
        installation = getattr(settings, 'INSTALLATION', None)
        if installation is not None:
            if installation == settings.PRODUCTION:
              request.ENV_IS_PRODUCTION = True
        request.ENV_IS_PRODUCTION = False
