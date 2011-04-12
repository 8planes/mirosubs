import logging
suspicious_logger = logging.getLogger("suspicious")

from django.http import  HttpResponseForbidden
from django.conf import settings
from django.utils.functional import wraps

def never_in_prod(view):
    """
    Decorator that makes sure the view is never called
    on production environment.
    This is useful for exposing some functionalities to testers /
    other staff members.
    """
    def wrapper(request, *args, **kwargs):
        installation = getattr(settings, 'INSTALLATION', None)
        not_allwed_msg = "Not allowed in production"
        if installation is not None and  installation == settings.PRODUCTION:
            suspicious_logger.warn("A failed attempt at staff only testers", extra={
                    'request': request,
                    'view': view.__name__,
                    'data': {
                        'username': request.user
                     },
            })
            return HttpResponseForbidden(not_allwed_msg)
        return view(request, *args, **kwargs)
    return wraps(view)(wrapper)
