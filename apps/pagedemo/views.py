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

import widget
from django.shortcuts import render_to_response
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.conf import settings

def pagedemo(request, file_name):
    context = widget.add_config_based_js_files(
        {}, settings.JS_WIDGETIZER, 'mirosubs-widgetizer.js')
    context['embed_js_url'] = \
        "http://{0}/embed{1}.js".format(
        Site.objects.get_current().domain,
        settings.EMBED_JS_VERSION)
    return render_to_response(
        'pagedemo/{0}.html'.format(file_name), 
        context, context_instance=RequestContext(request))

