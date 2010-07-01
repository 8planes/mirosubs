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

def relative_path(js_file):
    return "/site_media/js/%s" % js_file

def js_dependencies():
    js_files = list(settings.JS_ONSITE)
    js_files.append('widget/testing/stubvideoplayer.js');
    return [relative_path(js_file) for js_file in js_files]

def jsdemo(request, file_name):
    return render_to_response(
        'jsdemo/{0}.html'.format(file_name), 
        widget.add_js_files({}, False, js_dependencies()),
        context_instance=RequestContext(request))

