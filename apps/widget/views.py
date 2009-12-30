from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from uuid import uuid4
from django.contrib.sites.models import Site
import simplejson as json

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def add_params(params=None):
    if params is None:
        params = {}
    params["js_use_compiled"] = settings.JS_USE_COMPILED
    if settings.JS_USE_COMPILED:
        params["js_dependencies"] = [full_path("mirosubs-compiled.js")]
    else:
        params["js_dependencies"] = [full_path(js_file) for js_file in settings.JS_RAW]
    params["site"] = Site.objects.get_current()
    return params

def embed(request):
    params = {}
    params['video_id'] = request.GET['video_id']
    if request.user.is_authenticated():
        params['username'] = request.user.username
    params['uuid'] = str(uuid4()).replace('-', '')
    return render_to_response('widget/embed.js', add_params(params), 
                              mimetype="text/javascript")

def save_captions(request):
    video_id = request.POST["xdp:video_id"];
    deleted_captions = json.loads(request.POST["xdp:deleted"]);
    inserted_captions = json.loads(request.POST["xdp:inserted"]);
    updated_captions = json.loads(request.POST["xdp:updated"]);

    # TODO: save caption work to database
    # for definition of json format, see mirosubs-captionwidget.js

    params = {}
    params['request_id'] = request.POST["xdpe:request-id"]
    params['dummy_uri'] = request.POST["xdpe:dummy-uri"]
    params['response_json'] = '{\\"response\\": \\"ok\\"}'
    return render_to_response('widget/save_captions_response.html',
                              add_params(params))
