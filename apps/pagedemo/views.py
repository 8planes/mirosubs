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
from apps.videos.views import _widget_params

class ExtraContextHelpers(object):

    def for_boingboing_regular(type=None, request=None):
        try:
            num = int(request.GET.get('num_items'))
        except (ValueError, TypeError):
            num = 30
        videos = Video.objects.filter(languages_count__gt=1).filter(videourl__type='Y')[:num]
        for v in videos:
            if  type != "embed":
                v.url = v.get_video_url().replace('watch?v=', 'v/')
            elif type and type == 'embed':
                v.widget_params = _widget_params(request, v, version_no=None, language= v.subtitlelanguage_set.all()[0])
                v.url = v.get_video_url()

        return {
            "videos": videos,
            "type": type,
                
        }
    
    def for_boingboing_widgetizer(request):
        return ExtraContextHelpers.__dict__["for_boingboing_regular"] (type="widgetizer",request=request)

    def for_boingboing_async_widgetizer(request):
        return ExtraContextHelpers.__dict__["for_boingboing_regular"] (type="widgetizerasync",request=request)

    def for_boingboing_embed(request):
        return ExtraContextHelpers.__dict__["for_boingboing_regular"] (type="embed", request=request)

    for_boingboing_widgetizer.template_name =  "boingboing_regular"
    for_boingboing_async_widgetizer.template_name =  "boingboing_regular"
    
        
    def for_many_videos_widgetizer(request=None, type=None):
        videos = Video.objects.filter(languages_count__gt=1).filter(videourl__type='Y')[:40]
        urls = [];
        for v in videos:
            if type and type =='widgetizer':
                urls.append(v.get_video_url().replace('watch?v=', 'v/') )
                
            else:
                urls.append(v.get_video_url())

        return {
            "urls": urls,
            "type": type,
                
        }

    def for_many_videos():
        return ExtraContextHelpers.__dict__["for_many_videos_widgetizer"] (type="widetizer")
    

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
        extra_ = ExtraContextHelpers.__dict__[ "for_%s" % file_name]
        context.update( extra_(request=request))
        file_name = getattr(extra_, "template_name", file_name)
    try:
        return render_to_response(
            'pagedemo/{0}.html'.format(file_name), 
            context, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404

