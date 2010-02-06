from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from uuid import uuid4
from django.contrib.sites.models import Site
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.http import HttpResponseRedirect
from videos import models
from datetime import datetime
import simplejson as json
import views
import widget
import logging

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

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
    null_widget = 'null' in request.GET
    return render_to_response('widget/embed.js', 
                              widget.js_context(request, video, null_widget),
                              mimetype="text/javascript",
                              context_instance = RequestContext(request))

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
                              widget.add_js_files(params))

# start of rpc methods

def start_editing(request, video_id):
    # three cases: either the video is locked, or it is owned by someone else 
    # already and doesn't allow community edits, or i can freely edit it.

    # django won't set a session cookie unless something is in session state.
    request.session["dummy"] = "a"

    video = models.Video.objects.get(video_id=video_id)
    if video.owner != None and video.owner != request.user:
        return { "can_edit": False, "owned_by" : video.owner.username }
    if not video.can_writelock(request.session.session_key):
        return { "can_edit": False, "locked_by" : video.writelock_owner_name }

    video.writelock(request)
    video.save()
    version_list = list(video.videocaptionversion_set.all())
    if len(version_list) == 0:
        new_version_no = 0
        existing_captions = []
    else:
        max_version = max(version_list, key=lambda v: v.version_no)
        new_version_no = max_version.version_no + 1
        existing_captions = models.VideoCaption.objects.filter(\
            version__id__exact = max_version.id)
    return { "can_edit" : True, \
             "version" : new_version_no, \
             "existing" : [caption_to_dict(caption) for 
                           caption in existing_captions] }

def update_video_lock(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    if video.can_writelock(request.session.session_key):
        video.writelock(request)
        video.save()
        return { "response" : "ok" }
    else:
        return { "response" : "failed" }        

def release_video_lock(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    if video.can_writelock(request):
        video.release_writelock()
        video.save()
    return { "response": "ok" }

def getMyUserInfo(request):
    if request.user.is_authenticated():
        return { "logged_in" : True,
                 "username" : request.user.username }
    else:
        return { "logged_in" : False }

def save_captions(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    if not video.can_writelock(request.session.session_key):
        return { "response" : "unlockable" }
    video.writelock(request)
    save_captions_impl(request, video, version_no, deleted, inserted, updated)
    return {"response" : "ok"}

def finished_captions(request, video_id, version_no, deleted, inserted, updated):
    video = models.Video.objects.get(video_id=video_id)
    if not video.can_writelock(request.session.session_key):
        return { "response" : "unlockable" }
    last_version = save_captions_impl(request, video, version_no, 
                                      deleted, inserted, updated)
    last_version.is_complete = True
    last_version.save()
    video.release_writelock()
    video.save()
    return { "response" : "ok" }

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}

def fetch_captions(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    last_version = video.last_video_caption_version()
    captions = list(last_version.videocaption_set.all())
    return [caption_to_dict(caption) for caption in captions]

# helpers
def caption_to_dict(caption):
    # TODO: this is essentially duplication.
    return { 'caption_id' : caption.caption_id, \
             'caption_text' : caption.caption_text, \
             'start_time' : caption.start_time, \
             'end_time' : caption.end_time }

def save_captions_impl(request, video, version_no, deleted, inserted, updated):
    if video.owner is None:
        video.owner = request.user
    video.save()
    last_version = video.last_video_caption_version()
    if last_version != None and last_version.version_no == version_no:
        current_version = last_version
    else:
        current_version = models.VideoCaptionVersion(video=video, 
                                                     version_no=version_no,
                                                     datetime_started=datetime.now(),
                                                     user=request.user)
        if last_version != None:
            current_version.is_complete = last_version.is_complete
            current_version.save()
            for caption in list(last_version.videocaption_set.all()):
                current_version.videocaption_set.add(
                    caption.duplicate_for(current_version))
        else:
            current_version.save()
    captions = current_version.videocaption_set
    for d in deleted:
        captions.remove(captions.get(caption_id=d['caption_id']))
    for u in updated:
        caption = captions.get(caption_id=u['caption_id'])
        caption.update_from(u)
        caption.save()
    for i in inserted:
        captions.add(models.VideoCaption(version=current_version,
                                         caption_id=i['caption_id'],
                                         caption_text=i['caption_text'],
                                         start_time=i['start_time'],
                                         end_time=i['end_time']))
    current_version.save()
    return current_version
