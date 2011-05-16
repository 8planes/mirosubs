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
from django.template import RequestContext, TemplateDoesNotExist
from django.conf import settings
from django.http import Http404
from apps.videos.models import Video

class ExtraContextHelpers(object):


    def for_many_videos_widgetizer(widgetized=True):
        videos = Video.objects.filter(languages_count__gt=1).filter(videourl__type='Y')[:40]
        urls = [];
        for v in videos:
            if widgetized:
                urls.append(v.get_video_url().replace('watch?v=', 'v/') )
            else:
                urls.append(v.get_video_url())

        return {
            "urls": urls
                
        }

    def for_many_videos():
        return ExtraContextHelpers.__dict__["for_many_videos_widgetizer"] (True)
    

def pagedemo(request, file_name):
    if bool(file_name) is False:
        return pagedemo(request, "index")
    context = widget.add_config_based_js_files(
        {}, settings.JS_WIDGETIZER, 'mirosubs-widgetizer.js')
    context['embed_js_url'] = \
        "http://{0}/embed{1}.js".format(
        Site.objects.get_current().domain,
        settings.EMBED_JS_VERSION)
    if hasattr(ExtraContextHelpers, "for_%s" % file_name):
        context.update( ExtraContextHelpers.__dict__[ "for_%s" % file_name]())
    try:
        return render_to_response(
            'pagedemo/{0}.html'.format(file_name), 
            context, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404

