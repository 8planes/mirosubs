from django.conf import settings

def media(request):
    """
    Adds media-related context variables to the context.

    """
    return {'MEDIA_URL': settings.MEDIA_URL, "MEDIA_URL_BASE": settings.MEDIA_URL_BASE}
