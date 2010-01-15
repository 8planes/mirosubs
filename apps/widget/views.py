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
from datetime import datetime
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
    if 'video_id' in request.GET:
        video = models.Video.objects.get(video_id=request.GET['video_id'])
    else:
        video_url = request.GET['video_url']
        try:
            video = models.Video.objects.get(video_url=video_url)
        except models.Video.DoesNotExist:
            video = models.Video(video_url=video_url, \
                                 allow_community_edits=False)
            video.save()
    params = {}
    if video.caption_state == models.NO_CAPTIONS:
        params['show_tab'] = 0
    elif video.caption_state == models.CAPTIONS_IN_PROGRESS:
        if request.user.is_authenticated and request.user == video.owner:
            params['show_tab'] = 1
        else:
            params['show_tab'] = 2
            params['owned_by'] = video.owner.username
    else:
        params['show_tab'] = 3        
    params.update({'request': request, \
                   'video_id': video.video_id, \
                   'video_url': video.video_url, \
                   'uuid': str(uuid4()).replace('-', '')})
    return render_to_response('widget/embed.js', add_params(params), \
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


# start of rpc methods
def start_editing(request, video_id):
    # three cases: either the video is locked, or it is owned by someone else 
    # already and doesn't allow community edits, or i can freely edit it.
    video = models.Video.objects.get(video_id=video_id)
    if video.owner != None and video.owner != request.user:
        return { "can_edit": False, "owned_by" : video.owner.name }
    if video.is_writelocked:
        if video.writelock_owner == None:
            lock_owner_name = "anonymous"
        else:
            lock_owner_name = video.writelock_owner.username
        return { "can_edit": False, "locked_by" : lock_owner_name }
    if request.user.is_authenticated():
        video.owner = request.user
        video.writelock_owner = request.user
    else:
        video.writelock_owner = None
    video.writelock_time = datetime.now()
    video.save()
    version_list = list(video.videocaptionversion_set.all())
    if len(version_list) == 0:
        new_version_no = 0
        existing_captions = []
    else:
        max_version = max(version_list, key=version_no)
        new_version_no = max_version.version_no + 1
        existing_captions = models.VideoCaption.objects.filter(\
            version__id__exact == max_version.id)
    return { "can_edit" : True, \
             "version" : new_version_no, \
             "existing" : [caption_to_dict(caption) for 
                           caption in existing_captions] }

def update_lock(request, video_id):
    ok_response = { "response" : "ok" }
    failed_response = { "response" : "failed" }
    video = models.Video.objects.get(id=video_id)
    user = request.user if request.user.is_authenticated else None
    if video.can_writelock(user):
        video.writelock_time = datetime.now()
        video.writelock_owner = user
        video.save()
        return { "response" : "ok" }
    else:
        return { "repsonse" : "failed" }        

def getMyUserInfo(request):
    if request.user.is_authenticated:
        return { "logged_in" : True,
                 "username" : request.user.username }
    else:
        return { "logged_in" : False }

def save_captions(request, video_id, version_no, deleted, inserted, updated):
    # TODO: set me as the owner of the video if video.owner is currently None
    # TODO: create VideoCaptionVersion, if necessary. Be sure to copy captions from last.
    # TODO: save caption work to database
    return {"response" : "ok"}

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}

# helpers
def caption_to_dict(caption):
    # TODO: this is essentially duplication.
    return { 'caption_id' : caption.caption_id, \
             'caption_text' : caption.caption_text, \
             'start_time' : caption.start_time, \
             'end_time' : caption.end_time }
