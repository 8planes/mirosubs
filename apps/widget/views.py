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

import time

from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render_to_response, redirect
from django.utils.http import cookie_date
from django.contrib.sites.models import Site
from django.template import RequestContext
from videos import models
from widget.srt_subs import captions_and_translations_to_srt, captions_to_srt, SSASubtitles
import simplejson as json
from simplejson.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import widget
from django.shortcuts import get_object_or_404
from widget.rpc import add_general_settings
from widget.rpc import Rpc
from widget.null_rpc import NullRpc
from django.utils.encoding import iri_to_uri, DjangoUnicodeDecodeError
from django.db.models import ObjectDoesNotExist
from uslogging.models import WidgetDialogCall
from auth.models import CustomUser
from django.contrib.admin.views.decorators import staff_member_required

rpc_views = Rpc()
null_rpc_views = NullRpc()

def embed(request, version_no=''):
    """
    This is for serving embed when in development since the compilation
    with the media url hasn't taken place.
    Public clients will use the url : SITE_MEDIA/js/embed.js
    """
    context = widget.add_offsite_js_files({})
    if bool(version_no) is False:
        version_no = ""
    return render_to_response('widget/embed{0}.js'.format(version_no), 
                              context,
                              context_instance=RequestContext(request),
                              mimetype='text/javascript')

def widget_public_demo(request):
    context = widget.add_onsite_js_files({})
    return render_to_response('widget/widget_public_demo.html', context,
                              context_instance=RequestContext(request))

def onsite_widget(request):
    """Used for subtitle dialog"""
    context = widget.add_config_based_js_files(
        {}, settings.JS_API, 'mirosubs-api.js')
    config = request.GET.get('config', '{}')

    try:
        config = json.loads(config)
    except (ValueError, KeyError):
        raise Http404

    if 'HTTP_REFERER' in request.META:
        config['returnURL'] = request.META['HTTP_REFERER']

    if not config.get('nullWidget'): 
        video_id = config.get('videoID')

        if not video_id:
            raise Http404

        video = get_object_or_404(models.Video, video_id=video_id)

        if not 'returnURL' in config:
            config['returnURL'] = video.get_absolute_url()

        if not 'effectiveVideoURL' in config:
            config['effectiveVideoURL'] = video.get_video_url()

    context['widget_params'] = json.dumps(config)
    general_settings = {}
    add_general_settings(request, general_settings)
    context['general_settings'] = json.dumps(general_settings)
    return render_to_response('widget/onsite_widget.html',
                              context,
                              context_instance=RequestContext(request))

def widget_demo(request):
    context = {}
    context['js_use_compiled'] = settings.COMPRESS_MEDIA
    context['site_url'] = 'http://{0}'.format(
        request.get_host())
    if 'video_url' not in request.GET:
        context['help_mode'] = True
    else:
        context['help_mode'] = False
        spaces = ' ' * 9
        params = base_widget_params(request)
        context['embed_js_url'] = \
            "http://{0}/embed{1}.js".format(
            Site.objects.get_current().domain,
            settings.EMBED_JS_VERSION)
        context['widget_params'] = params
    return render_to_response('widget/widget_demo.html', 
                              context,
                              context_instance=RequestContext(request))

def video_demo(request, template):
    context = widget.add_config_based_js_files(
        {}, settings.JS_WIDGETIZER, 'mirosubs-widgetizer.js')
    context['embed_js_url'] = \
        "http://{0}/embed{1}.js".format(
        Site.objects.get_current().domain,
        settings.EMBED_JS_VERSION)
    return render_to_response(
        'widget/{0}_demo.html'.format(template), 
        context,
        context_instance=RequestContext(request))
    

def widgetize_demo(request, page_name):
    context = widget.add_config_based_js_files(
        {}, settings.JS_WIDGETIZER, 'mirosubs-widgetizer.js')
    return render_to_response('widget/widgetize_demo/{0}.html'.format(page_name),
                              context,
                              context_instance=RequestContext(request))

def statwidget_demo(request):
    js_files = ['http://{0}/widget/statwidgetconfig.js'.format(
            Site.objects.get_current().domain)]
    js_files.append('{0}js/statwidget/statwidget.js'.format(
            settings.MEDIA_URL))
    context = widget.add_js_files({}, settings.COMPRESS_MEDIA,
                               settings.JS_OFFSITE,
                               'mirosubs-statwidget.js',
                               full_path_js_files=js_files)
    return render_to_response('widget/statwidget_demo.html',
                              context,
                              context_instance=RequestContext(request))

def api_demo(request):
    context = widget.add_config_based_js_files(
        {}, settings.JS_API, 'mirosubs-api.js')
    return render_to_response('widget/api_demo.html',
                              context,
                              context_instance=RequestContext(request))

@staff_member_required
def save_emailed_translations(request):
    if request.method == "GET":
        return render_to_response(
            'widget/save_emailed_translations.html',
            context_instance=RequestContext(request))
    else:
        draft = models.SubtitleDraft.objects.get(pk=request.POST['draft_pk'])
        user = CustomUser.objects.get(pk=request.POST['user_pk'])
        subs = json.loads(request.POST['sub_text'])
        draft.subtitle_set.all().delete()
        for sub in subs:
            subtitle = models.Subtitle(
                draft=draft,
                subtitle_id=sub['subtitle_id'],
                subtitle_text=sub['text'])
            subtitle.save()
        draft = models.SubtitleDraft.objects.get(pk=draft.pk)
        rpc_views.save_finished(draft, user)
        return redirect(draft.video.video_link())        

def base_widget_params(request, extra_params={}):
    params = {}
    params['video_url'] = request.GET.get('video_url')
    if request.GET.get('null_widget') == 'true':   
        params['null_widget'] = True
    if request.GET.get('debug_js') == 'true':
        params['debug_js'] = True
    if request.GET.get('subtitle_immediately') == 'true':
        params['subtitle_immediately'] = True
    if request.GET.get('translate_immediately') == 'true':
        params['translate_immediately'] = True    
    if request.GET.get('base_state') is not None:
        params['base_state'] = json.loads(request.GET['base_state'])
    if request.GET.get('video_config') is not None:
        params['video_config'] = json.loads(request.GET['video_config'])
    params.update(extra_params)
    return json.dumps(params)[1:-1]

def download_subtitles(request, handler=SSASubtitles):
    #FIXME: use GenerateSubtitlesHandler
    video_id = request.GET.get('video_id')
    lang_id = request.GET.get('lang_pk')
    
    if not video_id:
        #if video_id == None, Video.objects.get raise exception. Better show 404
        #because video_id is required
        raise Http404
    
    video = get_object_or_404(models.Video, video_id=video_id)
    
    subtitles = []
    if not lang_id:
        # if no language is passed, assume it's the original one
        language  = video.subtitle_language()
    else:    
        try:
            language = video.subtitlelanguage_set.get(pk=lang_id)
        except ObjectDoesNotExist:

            raise Http404
    
    version = language and language.version()
    if not version:
        raise Http404    
    
    h = handler.create(version, video, language)
    response = HttpResponse(unicode(h), mimetype="text/plain")
    original_filename = '%s.%s' % (video.lang_filename(language), h.file_type)
    
    if not 'HTTP_USER_AGENT' in request.META or u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % original_filename.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        try:
            original_filename.encode('ascii')
        except UnicodeEncodeError:
            original_filename = 'subtitles.' + h.file_type
            
        filename_header = 'filename=%s' % original_filename
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % iri_to_uri(original_filename.encode('utf-8'))
    
    response['Content-Disposition'] = 'attachment; ' + filename_header
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

def _is_loggable(method):
    return method in ['start_editing', 'fork', 'save_subtitles', 'finished_subtitles']

@csrf_exempt
def rpc(request, method_name, null=False):
    if method_name[:1] == '_':
        return HttpResponseServerError('cant call private method')
    _log_call(request.browser_id, method_name, request.POST.copy())
    args = { 'request': request }
    try:
        for k, v in request.POST.items():
            args[k.encode('ascii')] = json.loads(v)
    except UnicodeEncodeError:
        return HttpResponseServerError('non-ascii chars received')
    except JSONDecodeError:
        return HttpResponseServerError('invalid json')
    rpc_module = null_rpc_views if null else rpc_views
    try:
        func = getattr(rpc_module, method_name)
    except AttributeError:
        return HttpResponseServerError('no method named ' + method_name)

    try:
        result = func(**args)
    except TypeError:
        result = {'error': 'Incorrect number of arguments'}
    
    user_message = result and result.pop("_user_message", None)
    response = HttpResponse(json.dumps(result), "application/json")
    if user_message is not None:
        response.set_cookie( "_user_message", user_message["body"], expires= cookie_date(time.time() +6), path="/")
    return response

@csrf_exempt
def xd_rpc(request, method_name, null=False):
    _log_call(request.browser_id, method_name, request.POST.copy())
    args = { 'request' : request }
    for k, v in request.POST.items():
        if k[0:4] == 'xdp:':
            args[k[4:].encode('ascii')] = json.loads(v)
    rpc_module = null_rpc_views if null else rpc_views
    func = getattr(rpc_module, method_name)
    result = func(**args)
    params = {
        'request_id' : request.POST['xdpe:request-id'],
        'dummy_uri' : request.POST['xdpe:dummy-uri'],
        'response_json' : json.dumps(result) }
    return render_to_response('widget/xd_rpc_response.html',
                              widget.add_offsite_js_files(params), 
                              context_instance = RequestContext(request))

def jsonp(request, method_name, null=False):
    _log_call(request.browser_id, method_name, request.GET.copy())
    callback = request.GET.get('callback', 'callback')
    args = { 'request' : request }
    for k, v in request.GET.items():
        if k != 'callback':
            args[k.encode('ascii')] = json.loads(v)
    rpc_module = null_rpc_views if null else rpc_views
    func = getattr(rpc_module, method_name)
    result = func(**args)
    return HttpResponse(
        "{0}({1});".format(callback, json.dumps(result)),
        "text/javascript")

def _log_call(browser_id, method_name, request_args):
    if method_name in ['start_editing', 'fork', 'set_title', 
                       'save_subtitles', 'finished_subtitles']:
        call = WidgetDialogCall(
            browser_id=browser_id,
            method=method_name,
            request_args=request_args)
        call.save()
