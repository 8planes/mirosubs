from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from uuid import uuid1


def add_params(params=None):
    if params is None:
        params = {}
    params["js_use_compiled"] = settings.JS_USE_COMPILED
    params["js_dependencies"] = settings.JS_DEPENDENCIES
    return params

def embed(request):
    params = {}
    params['video_id'] = request.GET['video_id']
    if request.user.is_authenticated():
        params['username'] = request.user.username
    params['uuid'] = str(uuid1()).replace('-', '')
    return render_to_response('widget/embed.js', add_params(params), 
                              mimetype="text/javascript")

def save_captions(request):
    params = {}
    params['request_id'] = request.POST["xdpe:request-id"]
    params['dummy_uri'] = request.POST["xdpe:dummy-uri"]
    params['response_json'] = "{'response': 'ok'}"
    return render_to_response('widget/save_captions_response.html',
                              add_params(params))
