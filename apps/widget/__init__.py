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

from uuid import uuid4
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.sites.models import Site
import simplejson as json

LANGUAGES_MAP = dict(LANGUAGES)

def embed_context():
    return { 'js_file': (full_path('js/mirosubs-offsite-compiled.js') 
                         if settings.COMPRESS_MEDIA else 
                         full_path(settings.JS_OFFSITE[-1])) }

def full_path(js_file):
    return "{0}{1}".format(settings.MEDIA_URL, js_file)

def add_offsite_js_files(context):
    """ Adds variables necessary for _js_dependencies.html """
    return add_js_files(context, settings.COMPRESS_MEDIA, 
                        settings.JS_OFFSITE, 
                        'js/mirosubs-offsite-compiled.js')

def add_onsite_js_files(context):
    """ Adds variables necessary for _js_onsite_dependencies.html """
    return add_js_files(context, settings.COMPRESS_MEDIA, 
                        settings.JS_ONSITE, 
                        'js/mirosubs-onsite-compiled.js')

def add_config_based_js_files(context, files, compiled_file_name):
    js_files = []
    if settings.COMPRESS_MEDIA:
        js_files.append(full_path(compiled_file_name))
    else:
        js_files.append('http://{0}/widget/config.js'.format(
                Site.objects.get_current().domain))
        js_files.extend(
            [full_path(js_file) for js_file 
             in files])

    context['js_use_compiled'] = settings.COMPRESS_MEDIA
    context['js_dependencies'] = js_files
    return context



def add_js_files(context, use_compiled, js_files, compiled_file_name=None, full_path_js_files=[]):
    context["js_use_compiled"] = use_compiled
    if use_compiled:
        # might change in future when using cdn to serve static js
        context["js_dependencies"] = [full_path(compiled_file_name)]
    else:
        context["js_dependencies"] = [full_path(js_file) for js_file in js_files] + full_path_js_files
    return context;    

def language_to_map(code, name, percent_done=None):
    map = { 'code': code, 'name': name };
    if percent_done is not None:
        map['percent_done'] = percent_done
    return map
