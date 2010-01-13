from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from uuid import uuid4
from django.contrib.sites.models import Site
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.http import HttpResponseRedirect
from widget import models
import simplejson as json
import views

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def add_params(params=None):
    if params is None:
        params = {}
    params["js_use_compiled"] = settings.JS_USE_COMPILED
    if settings.JS_USE_COMPILED:
        # might change in future when using cdn to serve static js
        params["js_dependencies"] = [full_path("mirosubs-compiled.js")]
    else:
        params["js_dependencies"] = [full_path(js_file) for js_file in settings.JS_RAW]
    params["site"] = Site.objects.get_current()
    return params

def embed(request):
    # just temporary
    video = models.Video.objects.get(id=1)
    params = {}
    params['request'] = request
    params['video_id'] = request.GET['video_id']
    params['video_url'] = video.video_url;
    params['has_subtitles'] = False
    params['has_subtitles_var'] = 'false'
    params['uuid'] = str(uuid4()).replace('-', '')
    return render_to_response('widget/embed.js', add_params(params), 
                              mimetype="text/javascript")

def rpc(request, method_name):
    args = { 'request': request }
    for k, v in request.POST.items():
        args[k.encode('ascii')] = json.loads(v)
    func = getattr(views, method_name)
    result = func(**args)
    return HttpResponse(json.dumps(result), "application/json")

def xd_rpc(request, method_name):
    args = { 'request' : request }
    for k, v in request.POST.items():
        if k[0:4] == 'xdp:':
            args[k[4:].encode('ascii')] = json.loads(v)
    func = getattr(views, method_name)
    result = func(**args)
    params = {
        'request_id' : request.POST['xdpe:request-id'],
        'dummy_uri' : request.POST['xdpe:dummy-uri'],
        'response_json' : json.dumps(result) }
    return render_to_response('widget/xd_rpc_response.html',
                              add_params(params))

def getMyUserInfo(request):
    if request.user.is_authenticated:
        return { "logged_in" : True,
                 "username" : request.user.username }
    else:
        return { "logged_in" : False }

def save_captions(request, video_id, deleted, inserted, updated):
    # TODO: save caption work to database
    return {"response" : "ok"}

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}
