# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import update_wrapper
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import simplejson as json
from django.core.mail import mail_admins
from django.conf import settings
import re
import htmllib
from subtitles import SubtitleParserError, SubtitleParser, TxtSubtitleParser, YoutubeSubtitleParser, \
    TtmlSubtitleParser, SrtSubtitleParser, SbvSubtitleParser, SsaSubtitleParser
import traceback, sys
from django.contrib.auth.decorators import user_passes_test

def is_staff(user):
    return user.is_authenticated() and user.is_staff and user.is_active

check_is_staff = user_passes_test(is_staff)

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return update_wrapper(wrapper, func)
    return renderer

def render_to_json(func):
    def wrapper(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        
        if isinstance(result, HttpResponse):
            return result
        
        json = simplejson.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json, mimetype="application/json")
    return update_wrapper(wrapper, func)

def get_page(request):
    page = request.GET.get('page')
    if not page == 'last':
        try:
            page = int(page)
        except (ValueError, TypeError, KeyError):
            page = 1
    return page

def get_pager(objects, on_page=15, page='1', orphans=0):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(objects, on_page, orphans=orphans)
    try:
        page = paginator.page(int(page))
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    return page

def send_templated_email(to, subject, body_template, body_dict, 
                         from_email=None, ct="html", fail_silently=False):
    if not isinstance(to, list): to = [to]
    if not from_email: from_email = settings.DEFAULT_FROM_EMAIL

    message = render_to_string(body_template, body_dict)
    bcc = settings.EMAIL_BCC_LIST
    email = EmailMessage(subject, message, from_email, to, bcc=bcc)
    email.content_subtype = ct
    email.send(fail_silently)

def catch_exception(exceptions, subject="", default=None):
    if not isinstance(exceptions, (list, tuple)):
        exceptions = (exceptions,)

    def catch_exception_func(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions, e:
                if settings.DEBUG:
                    print 'Redis error %s' % e
                else:
                    body = '\n'.join(traceback.format_exception(*sys.exc_info()))
                    mail_admins(subject, body, fail_silently=True)
                return default
        return update_wrapper(wrapper, func)
    return catch_exception_func