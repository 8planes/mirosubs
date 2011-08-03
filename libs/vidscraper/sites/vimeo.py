# Miro - an RSS based video player application
# Copyright 2009 - Participatory Culture Foundation
# 
# This file is part of vidscraper.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import re
import urllib

from lxml import builder
from lxml import etree
from lxml.html import builder as E
from lxml.html import tostring
import oauth2
import simplejson

from vidscraper.decorators import provide_shortmem, parse_url, returns_unicode
from vidscraper import util
from vidscraper.errors import Error
from django.conf import settings

class VimeoError(Error):
    pass

VIMEO_API_URL = 'http://vimeo.com/api/rest/v2/'

EMaker = builder.ElementMaker()
EMBED = EMaker.embed

EMBED_WIDTH = 425
EMBED_HEIGHT = 344

def get_shortmem(url):
    shortmem = {}
    video_id = VIMEO_REGEX.match(url).groupdict()['video_id']
    url = '%s?%s' % (VIMEO_API_URL,
                     urllib.urlencode({
                'method': 'vimeo.videos.getInfo',
                'format': 'json',
                'video_id': video_id}))
    consumer = oauth2.Consumer(settings.VIMEO_API_KEY, settings.VIMEO_API_SECRET)
    client = oauth2.Client(consumer)
    backoff = util.random_exponential_backoff(2)

    for i in range(3):
        try:
            api_raw_data = client.request(url)[1]
            api_data = simplejson.loads(api_raw_data)
        except Exception, e:
            continue
        else:
            if api_data.get('stat') == u'fail':
                error = u'Vimeo API error'
                try:
                    error += ': %s' % api_data['err']['expl']
                except KeyError:
                    pass
                raise VimeoError(error)

            if 'video' in api_data:
                shortmem['api_data'] = api_data['video'][0]
                break
            else:
                #this is hack to get info from Vimeo API. For some video it return strange error in response
                try:
                    data = api_data['backtrace'][1]['object']["_valStack"][1]["children"]
                    if 'description' in data and 'title' in data:
                        shortmem['api_data'] = data
                        break                        
                except (KeyError, IndexError):
                    pass
                    
        backoff.next()
    return shortmem

def parse_api(scraper_func, shortmem=None):
    def new_scraper_func(url, shortmem={}, *args, **kwargs):
        if not shortmem:
            shortmem = get_shortmem(url)
        return scraper_func(url, shortmem=shortmem, *args, **kwargs)
    return new_scraper_func

@parse_api
@returns_unicode
def scrape_title(url, shortmem={}):
    try:
        return shortmem['api_data']['title'] or u''
    except KeyError:
        return u''

@parse_api
@returns_unicode
def scrape_description(url, shortmem={}):
    try:
        description = shortmem['api_data']['description']
    except KeyError:
        description = ''
    return util.clean_description_html(description)

@parse_url
@returns_unicode
def scrape_file_url(url, shortmem={}):
    vimeo_match = VIMEO_REGEX.match(url)
    video_id = vimeo_match.group(2)
    video_data_url = (
        u"http://www.vimeo.com/moogaloop/load/clip:%s" % video_id)
    vimeo_data = None
    for i in range(5):
        try:
            vimeo_data = etree.parse(video_data_url)
        except etree.XMLSyntaxError:
            pass
        else:
            break
    if not vimeo_data:
        return ''
    req_sig = vimeo_data.find('request_signature')
    req_sig_expires = vimeo_data.find('request_signature_expires')
    if req_sig is None or req_sig_expires is None:
        return ''
    return "http://www.vimeo.com/moogaloop/play/clip:%s/%s/%s/?q=sd" % (
        video_id, req_sig.text, req_sig_expires.text)

def file_url_is_flaky(url, shortmem={}):
    return True

@returns_unicode
def get_flash_enclosure_url(url, shortmem={}):
    vimeo_match = VIMEO_REGEX.match(url)
    video_id = vimeo_match.group(2)
    return 'http://vimeo.com/moogaloop.swf?clip_id=' + video_id

@returns_unicode
def get_embed(url, shortmem={}, width=EMBED_WIDTH, height=EMBED_HEIGHT):
    get_dict = {'server': 'vimeo.com',
                'show_title': 1,
                'show_byline': 1,
                'show_portrait': 0,
                'color': '',
                'fullscreen': 1}

    get_dict['clip_id'] = VIMEO_REGEX.match(url).groupdict()['video_id']

    flash_url = 'http://vimeo.com/moogaloop.swf?' + urllib.urlencode(get_dict)

    object_children = (
        E.PARAM(name="allowfullscreen", value="true"),
        E.PARAM(name="allowscriptaccess", value="always"),
        E.PARAM(name="movie", value=flash_url),
        EMBED(src=flash_url,
              type="application/x-shockwave-flash",
              allowfullscreen="true",
              allowscriptaccess="always",
              width=str(EMBED_WIDTH), height=str(EMBED_HEIGHT)))
    main_object = E.OBJECT(
        width=str(EMBED_WIDTH), height=str(EMBED_HEIGHT), *object_children)

    return tostring(main_object)

@parse_api
@returns_unicode
def get_thumbnail_url(url, shortmem={}):
    max_size = 0
    url = None
    try:
        for thumbnail in shortmem['api_data']['thumbnails']['thumbnail']:
            if 'thumbnails/defaults' in thumbnail['_content']:
                if not url:
                    url = thumbnail['_content'] # use it only if we don't have a
                                                # better thumbnail
                continue
            size = int(thumbnail['width']) * int(thumbnail['height'])
            if size > max_size:
                max_size = size
                url = thumbnail['_content']
    except KeyError:
        pass
    return url

@parse_api
@returns_unicode
def get_small_thumbnail_url(url, shortmem={}):
    url = None
    try:
        url = shortmem['api_data']['thumbnails']['thumbnail'][1]['_content']
    except (KeyError, IndexError):
        pass
    return url

@parse_api
@returns_unicode
def get_user(url, shortmem={}):
    return shortmem['api_data']['owner']['display_name']

@parse_api
@returns_unicode
def get_user_url(url, shortmem={}):
    return shortmem['api_data']['owner']['profileurl']

@parse_api
def scrape_publish_date(url, shortmem={}):
    return datetime.datetime.strptime(
        shortmem['api_data']['upload_date'], '%Y-%m-%d %H:%M:%S')

VIMEO_REGEX = re.compile(r'https?://([^/]+\.)?vimeo.com/(channels/[\w]+[#|/])?(?P<video_id>\d+)')
SUITE = {
    'regex': VIMEO_REGEX,
    'funcs': {
        'title': scrape_title,
        'description': scrape_description,
        'publish_date': scrape_publish_date,
        'file_url': scrape_file_url,
        'file_url_is_flaky': file_url_is_flaky,
        'flash_enclosure_url': get_flash_enclosure_url,
        'publish_date': scrape_publish_date,
        'embed': get_embed,
        'thumbnail_url': get_thumbnail_url,
        'user': get_user,
        'user_url': get_user_url},
    'order': ['title', 'description', 'file_url', 'embed']}
            
