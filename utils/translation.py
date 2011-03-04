from django.utils.translation import get_language, ugettext as _
from django.conf import settings
from django.core.cache import cache
from django.utils import simplejson as json
import time
from django.utils.http import cookie_date
from translation_names import LANGUAGE_NAMES, ORIGINAL_LANGUAGE_NAMES

SUPPORTED_LANGUAGES_DICT = dict(settings.ALL_LANGUAGES)

def get_simple_languages_list(with_empty=False):
    cache_key = 'simple-langs-cache-%s' % get_language() 
    languages = cache.get(cache_key)   
    if not languages:
        languages = []
        
        for val, name in settings.ALL_LANGUAGES:
            languages.append((val, _(name)))
        languages.sort(key=lambda item: item[1])
        cache.set(cache_key, languages, 60*60)
    if with_empty:
        languages = [('', '---------')]+languages
    return languages
   
def get_languages_list(with_empty=False):
    cache_key = 'langs-cache-%s' % get_language() 
    
    languages = cache.get(cache_key)
    
    if not languages:
        languages = []
        
        for val, name in settings.ALL_LANGUAGES:
            if val in ORIGINAL_LANGUAGE_NAMES:
                name = u'%s (%s)' % (_(name), ORIGINAL_LANGUAGE_NAMES[val])
            else:
                name = _(name)
            languages.append((val, name))
        languages.sort(key=lambda item: item[1])
        cache.set(cache_key, languages, 60*60)
    if with_empty:
        languages = [('', '---------')]+languages
    return languages

from django.utils.translation.trans_real import parse_accept_lang_header
from django.utils import translation

def get_user_languages_from_request(request, only_supported=False, with_names=False):
    languages = []
    if request.user.is_authenticated():
        languages = [l.language for l in request.user.userlanguage_set.all()]    
        
    if not languages:
        languages = languages_from_request(request)

    if only_supported:
        for item in languages:
            if not item in SUPPORTED_LANGUAGES_DICT and \
                not item.split('-')[0] in SUPPORTED_LANGUAGES_DICT:
                    languages.remove(item)

    return with_names and languages_with_names(languages) or languages

def set_user_languages_to_cookie(response, languages):
    max_age = 60*60*24
    response.set_cookie(
        settings.USER_LANGUAGES_COOKIE_NAME,
        json.dumps(languages), 
        max_age=max_age,
        expires=cookie_date(time.time() + max_age))

def get_user_languages_from_cookie(request):
    try:
        langs = json.loads(request.COOKIES.get(settings.USER_LANGUAGES_COOKIE_NAME, '[]'))
        for l in langs:
            if not l in SUPPORTED_LANGUAGES_DICT:
                langs.remove(l)
        return langs
    except (TypeError, ValueError):
        return []

def languages_from_request(request, only_supported=False, with_names=False):
    languages = []
    
    for l in get_user_languages_from_cookie(request):
        if not l in languages:
            languages.append(l)
    
    if not languages:
        trans_lang = translation.get_language()
        if not trans_lang in languages:
            languages.append(trans_lang)
        
        if hasattr(request, 'session'):
            lang_code = request.session.get('django_language', None)
            if lang_code is not None and not lang_code in languages:
                languages.append(lang_code)
                
        cookie_lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if cookie_lang_code and not cookie_lang_code in languages:
            languages.append(cookie_lang_code)
            
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')        
        for lang, val in parse_accept_lang_header(accept):
            if lang and lang != '*' and not lang in languages:
                languages.append(lang)
            
    if only_supported:
        for item in languages:
            if not item in SUPPORTED_LANGUAGES_DICT:
                languages.remove(item)
    
    return with_names and languages_with_names(languages) or languages

def languages_with_names(langs):
    output = {}
    for l in langs:
        try:
            output[l] = _(SUPPORTED_LANGUAGES_DICT[l])
        except KeyError:
            try:
                l = l.split('-')[0]
                output[l] = _(SUPPORTED_LANGUAGES_DICT[l])
            except KeyError:
                pass
    return output