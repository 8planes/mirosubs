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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.sites.models import Site
from django.template import RequestContext
from videos import models
from widget.srt_subs import captions_and_translations_to_srt, captions_to_srt
import simplejson as json
from widget import rpc as rpc_views
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import widget

def embed(request):
    context = widget.add_offsite_js_files({})
    return render_to_response('widget/embed.js', context,
                              context_instance=RequestContext(request),
                              mimetype='text/javascript')

def widget_public_demo(request):
    context = widget.add_onsite_js_files({})
    return render_to_response('widget/widget_public_demo.html', context,
                              context_instance=RequestContext(request))

def widget_demo(request):
    context = {}
    context['js_use_compiled'] = settings.JS_USE_COMPILED
    context['site_url'] = 'http://{0}'.format(
        request.get_host())
    if 'video_url' not in request.GET:
        context['help_mode'] = True
    else:
        context['help_mode'] = False
        spaces = ' ' * 9
        params = '{0}video_url: \'{1}\''.format(spaces, request.GET['video_url'])
        if request.GET.get('null_widget', None) == 'true':
            params += ',\n{0}null_widget: true'.format(spaces)
        if request.GET.get('debug_js', None) == 'true':
            params += ',\n{0}debug_js: true'.format(spaces)
        if request.GET.get('subtitle_immediately', None) == 'true':
            params += ',\n{0}subtitle_immediately: true'.format(spaces)
        if request.GET.get('translate_immediately', None) == 'true':
            params += ',\n{0}translate_immediately: true'.format(spaces)
        if request.GET.get('autoplay_language', None) is not None:
            params += ',\n{0}autoplay_language: \'{1}\''.format(
                spaces, request.GET['autoplay_language'])
        context['embed_js_url'] = \
            "http://{0}/embed.js".format(Site.objects.get_current().domain)
        context['widget_params'] = params
    return render_to_response('widget/widget_demo.html', 
                              context,
                              context_instance=RequestContext(request))

def srt(request):
    video = models.Video.objects.get(video_id=request.GET['video_id'])
    if 'lang_code' in request.GET:
        lang_code = request.GET['lang_code']
        response_text = captions_and_translations_to_srt(
            video.captions_and_translations(lang_code))
    else:
        response_text = captions_to_srt(
            list(video.captions().videocaption_set.all()))
    response = HttpResponse(response_text, mimetype="text/plain")
    response['Content-Disposition'] = \
        'attachment; filename={0}'.format(video.srt_filename)
    return response

def null_srt(request):
    # FIXME: possibly note duplication with srt, and fix that.
    video = models.Video.objects.get(video_id=request.GET['video_id'])
    if 'lang_code' in request.GET:
        lang_code = request.GET['lang_code']
        response_text = captions_and_translations_to_srt(
            video.null_captions_and_translations(request.user, lang_code))
    else:
        response_text = captions_to_srt(
            list(video.null_captions(request.user).videocaption_set.all()))
    response = HttpResponse(response_text, mimetype="text/plain")
    response['Content-Disposition'] = \
        'attachment; filename={0}'.format(video.srt_filename)
    return response

@csrf_exempt
def rpc(request, method_name):
    args = { 'request': request }
    for k, v in request.POST.items():
        args[k.encode('ascii')] = json.loads(v)
    func = getattr(rpc_views, method_name)
    result = func(**args)
    return HttpResponse(json.dumps(result), "application/json")

@csrf_exempt
def xd_rpc(request, method_name):
    args = { 'request' : request }
    for k, v in request.POST.items():
        if k[0:4] == 'xdp:':
            args[k[4:].encode('ascii')] = json.loads(v)
    func = getattr(rpc_views, method_name)
    result = func(**args)
    params = {
        'request_id' : request.POST['xdpe:request-id'],
        'dummy_uri' : request.POST['xdpe:dummy-uri'],
        'response_json' : json.dumps(result) }
    return render_to_response('widget/xd_rpc_response.html',
                              widget.add_offsite_js_files(params), 
                              context_instance = RequestContext(request))

def jsonp(request, method_name):
    callback = request.GET['callback']
    args = { 'request' : request }
    for k, v in request.GET.items():
        if k != 'callback':
            args[k.encode('ascii')] = json.loads(v)
    func = getattr(rpc_views, method_name)
    result = func(**args)
    return HttpResponse(
        "{0}({1});".format(callback, json.dumps(result)),
        "text/javascript")
