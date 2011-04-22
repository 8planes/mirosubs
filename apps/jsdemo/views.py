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
import sys
import logging

def js_dependencies():
    js_files = list(settings.JS_ONSITE)
    js_files.append('widget/testing/stubvideoplayer.js');
    return js_files

def jsdemo(request, file_name):
    if file_name == 'raise_exception':
        sys.stderr.write('I am also writing gratuitous text to stderr '
                         'just to see if stderr output ends up in log')
        raise Exception('gratuitous exception')
    elif file_name == 'log_error':
        logging.error(
            'log error test with extras',
            extra={
                'data': {
                    'important_message': 'adam is so awesome',
                    'the_temperature': 10 }
                })
    elif file_name == 'log_warning':
        logging.warning(
            'here is a warning, y\'all!',
            extra={
                'data': {
                    'what': 'what, what'
                    }
                })
    return render_to_response(
        'jsdemo/{0}.html'.format(file_name), 
        widget.add_js_files({}, False, js_dependencies()),
        context_instance=RequestContext(request))

