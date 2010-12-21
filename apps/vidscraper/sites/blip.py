# -*- test-case-name: vidscraper.tests.test_blip -*-anon
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

import re
import simplejson
import urllib

import feedparser
from lxml import builder

from vidscraper.decorators import (provide_shortmem, returns_unicode,
                                   returns_struct_time)
from vidscraper import errors, util, miroguide_util


EMaker = builder.ElementMaker()
EMBED = EMaker.embed

EMBED_WIDTH = 425
EMBED_HEIGHT = 344

def get_shortmem(url):
    shortmem = {}
    file_id = BLIP_REGEX.match(url).groupdict()['file_id']
    rss_url = 'http://blip.tv/file/%s?skin=rss' % file_id
    parsed = feedparser.parse(rss_url)
    if 'entries' not in parsed or not parsed.entries:
        shortmem['feed_item'] = None
    else:
        shortmem['feed_item'] = parsed['entries'][0]
    return shortmem

def parse_feed(scraper_func, shortmem=None):
    def new_scraper_func(url, shortmem={}, *args, **kwargs):
        if not shortmem:
            shortmem = get_shortmem(url)
        return scraper_func(url, shortmem=shortmem, *args, **kwargs)
    return new_scraper_func

def _fp_get(shortmem, key):
    """
    Feedparser sometimes strips off the blip_ prefix in its dictionary.  This
    function helps by checking both for us.
    """
    fp = shortmem['feed_item']
    return fp.get('blip_%s' % key,
                  fp.get(key))

@parse_feed
@returns_unicode
def get_thumbnail_url(url, shortmem={}):
    if _fp_get(shortmem, 'thumbnail_src'):
        return 'http://a.images.blip.tv/%s' % (
            _fp_get(shortmem, 'thumbnail_src'),)
    elif _fp_get(shortmem, 'smallthumbnail'):
        return _fp_get(shortmem, 'smallthumbnail')
    else:
        return _fp_get(shortmem, 'picture')


@parse_feed
@returns_unicode
def get_link(url, shortmem={}):
    return shortmem['feed_item'].link

@parse_feed
@returns_unicode
def scrape_title(url, shortmem={}):
    try:
        return shortmem['feed_item']['title']
    except KeyError:
        raise errors.FieldNotFound('Could not find the title field')


@parse_feed
@returns_unicode
def scrape_description(url, shortmem={}):
    if 'summary' in shortmem['feed_item']:
        description = shortmem['feed_item'].summary
    else:
        description = _fp_get(shortmem, 'puredescription')

    if description:
        return util.clean_description_html(description)
    else:
        return u''


@parse_feed
@returns_unicode
def scrape_file_url(url, shortmem={}):
    try:
        video_enclosure = miroguide_util.get_first_video_enclosure(
            shortmem['feed_item'])
        if video_enclosure is not None:
            return video_enclosure.get('url')
    except KeyError:
        raise errors.FieldNotFound('Could not find the feed_item field')


@parse_feed
@returns_struct_time
def scrape_publish_date(url, shortmem={}):
    # sure it's not exactly the publish date, but it's close
    try:
        return shortmem['feed_item'].updated_parsed
    except KeyError:
        raise errors.FieldNotFound('Could not find the publish_date field')

def get_embed(url, shortmem={}, width=EMBED_WIDTH, height=EMBED_HEIGHT):
    file_id = BLIP_REGEX.match(url).groupdict()['file_id']
    oembed_get_dict = {
            'url': 'http://blip.tv/file/%s' % file_id,
            'width': EMBED_WIDTH,
            'height': EMBED_HEIGHT}

    oembed_response = None
    for i in range(5):
        try:
            oembed_response = urllib.urlopen(
                'http://blip.tv/oembed/?' + urllib.urlencode(
                    oembed_get_dict)).read()
            break
        except IOError:
            pass

    if not oembed_response:
        return None

    # simplejson doesn't like the \' escape
    oembed_response = oembed_response.replace(r"\'", "'")

    # clean up the response, and check for a trailing ,
    oembed_response = oembed_response.replace('\n', '').replace('\t', '')
    if oembed_response.endswith(',}'):
        oembed_response = oembed_response[:-2] + '}'

    try:
        embed_code = simplejson.loads(oembed_response.decode('utf8'))['html']
    except (ValueError, KeyError):
        embed_code = None

    return embed_code

@parse_feed
def get_tags(url, shortmem={}):
    return [tag['term'] for tag in shortmem['feed_item'].tags]

@parse_feed
def get_user(url, shortmem={}):
    return _fp_get(shortmem, 'user')

@parse_feed
def get_user_url(url, shortmem={}):
    url = _fp_get(shortmem, 'showpage')
    if url.startswith('http://') or url.startswith('https://'):
        return url
    else:
        return 'http://%s' % (url,)

import httplib
from xml.dom import minidom

def video_file_url(file_id):
    rss_path = '/file/%s?skin=rss' % file_id
    conn = httplib.HTTPConnection("blip.tv")
    conn.request("GET", rss_path)
    response = conn.getresponse()
    body = response.read()
    xmldoc = minidom.parseString(body)
    media_content_elements = xmldoc.getElementsByTagName('media:content')
    return _best_flv(media_content_elements) or \
        _best_mp4(media_content_elements) or \
        _best_any(media_content_elements)

def _best_any(media_contents):
    f = lambda c: True
    return _best_by_height(media_contents, f)

def _best_mp4(media_contents):
    f = lambda c: c.getAttribute('type') in ['video/x-m4v', 'video/mp4']
    return _best_by_height(media_contents, f)

def _best_flv(media_contents):
    f = lambda c: c.getAttribute('type') == 'video/x-flv'
    return _best_by_height(media_contents, f)

def _best_by_height(media_contents, type_fn):
    best = None
    best_height = None
    HEIGHT = 360
    for content in media_contents:
        height = int(content.getAttribute('height') or 0)
        height_is_best = True if best is None else \
            abs(HEIGHT - height) < abs(HEIGHT - best_height)
        if type_fn(content) and height_is_best:
            best = content
            best_height = height
    return best and best.getAttribute('url')

BLIP_REGEX = re.compile(
    r'^https?://(?P<subsite>[a-zA-Z]+\.)?blip.tv/file/(?P<file_id>\d+)')
SUITE = {
    'regex': BLIP_REGEX,
    'funcs': {
        'link': get_link,
        'title': scrape_title,
        'description': scrape_description,
        'embed': get_embed,
        'file_url': scrape_file_url,
        'thumbnail_url': get_thumbnail_url,
        'tags': get_tags,
        'publish_date': scrape_publish_date,
        'user': get_user,
        'user_url': get_user_url}}
