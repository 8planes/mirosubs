# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)

from django.conf import settings
from django.core.urlresolvers import get_script_prefix
from django import template
from django.template import Node, Token, TemplateSyntaxError
from django.template import resolve_variable, defaulttags
from django.template.defaultfilters import stringfilter
from django.utils import translation
import localeurl.settings
from localeurl import utils

register = template.Library()


def chlocale(url, locale):
    """
    Changes the URL's locale prefix if the path is not locale-independent.
    Otherwise removes locale prefix.
    """
    script_prefix, path = strip_script_prefix(url)
    _, path = utils.strip_path(path)
    return utils.locale_url(path, locale)

chlocale = stringfilter(chlocale)
register.filter('chlocale', chlocale)


def rmlocale(url):
    """Removes the locale prefix from the URL."""
    script_prefix, path = strip_script_prefix(url)
    _, path = utils.strip_path(path)
    return ''.join([script_prefix, path])

rmlocale = stringfilter(rmlocale)
register.filter('rmlocale', rmlocale)


def locale_url(parser, token):
    """
    Renders the url for the view with another locale prefix. The syntax is
    like the 'url' tag, only with a locale before the view.

    Examples:
      {% locale_url "de" cal.views.day day %}
      {% locale_url "nl" cal.views.home %}
      {% locale_url "en-gb" cal.views.month month as month_url %}
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments:"
                " the locale and a view" % bits[0])
    urltoken = Token(token.token_type, bits[0] + ' ' + ' '.join(bits[2:]))
    urlnode = defaulttags.url(parser, urltoken)
    return LocaleURLNode(bits[1], urlnode)

class LocaleURLNode(Node):
    def __init__(self, locale, urlnode):
        self.locale = locale
        self.urlnode = urlnode

    def render(self, context):
        locale = resolve_variable(self.locale, context)
        path = self.urlnode.render(context)
        if self.urlnode.asvar:
            self.urlnode.render(context)
            context[self.urlnode.asvar] = chlocale(context[self.urlnode.asvar],
                    locale)
            return ''
        else:
            return chlocale(path, locale)

register.tag('locale_url', locale_url)

def strip_script_prefix(url):
    """
    Strips the SCRIPT_PREFIX from the URL. Because this function is meant for
    use in templates, it assumes the URL starts with the prefix.
    """
    assert url.startswith(get_script_prefix()), \
            "URL does not start with SCRIPT_PREFIX: %s" % url
    pos = len(get_script_prefix()) - 1
    return url[:pos], url[pos:]
