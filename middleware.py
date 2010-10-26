from django.conf import settings
import random
from django.utils.hashcompat import sha_constructor
from django.utils.cache import patch_vary_headers

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
            request.META["UUID_COOKIE"] = request.COOKIES[UUID_COOKIE_NAME]
        except KeyError:
            # No cookie, so create one.  This will be sent with the next
            # response.
            request.META["UUID_COOKIE"] = _get_new_csrf_key()

    def process_response(self, request, response):
        response.set_cookie(UUID_COOKIE_NAME,
                request.META["UUID_COOKIE"], max_age = 60 * 60 * 24 * 7 * 52 * 10,
                domain=UUID_COOKIE_DOMAIN)
        # Content varies with the CSRF cookie, so set the Vary header.
        patch_vary_headers(response, ('Cookie',))
        return response            