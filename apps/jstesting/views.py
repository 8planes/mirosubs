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

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
import widget
import simplejson as json


def js_dependencies():
    js_files = list(settings.JS_API)
    js_files.append('widget/testing/stubvideoplayer.js')
    js_files.append('widget/testing/events.js')
    return js_files

def jstest(request, file_name):
    if file_name == 'alltests':
        template = 'jstesting/alltests.html'
    else:
        template = 'jstesting/{0}.js'.format(file_name)
    context = {
        'languages': json.dumps(settings.ALL_LANGUAGES) }
    return render_to_response(
        template,
        widget.add_js_files(context, False, js_dependencies()),
        context_instance=RequestContext(request))
