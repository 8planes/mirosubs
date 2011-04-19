# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)

django_reverse = None

def patch_reverse():
    global django_reverse
    from django.conf import settings
    from django.core import urlresolvers
    from django.utils import translation
    import localeurl.settings
    from localeurl import utils    

    if not django_reverse and localeurl.settings.URL_TYPE == 'path_prefix' and settings.USE_I18N:
        def reverse(viewname, urlconf=None, args=[], kwargs={}, prefix=None, current_app=None):
            kwargs = kwargs or {}
            locale = kwargs.pop('locale', translation.get_language())
            path = django_reverse(viewname, urlconf, args, kwargs, prefix, current_app)
            if locale == '':
                return path
            return utils.locale_url(path, utils.supported_language(locale))
        
        django_reverse = urlresolvers.reverse
        urlresolvers.reverse = reverse