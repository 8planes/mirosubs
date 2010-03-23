from uuid import uuid4
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from uuid import uuid4
from django.contrib.sites.models import Site
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.http import HttpResponseRedirect
from videos import models
from videos.models import VIDEO_SESSION_KEY
from datetime import datetime
import simplejson as json
import views
import widget
import logging

LANGUAGES_MAP = dict(LANGUAGES)

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def embed(request):
    if 'video_id' in request.GET:
        video = models.Video.objects.get(video_id=request.GET['video_id'])
    elif 'youtube_videoid' in request.GET:
        youtube_videoid = request.GET['youtube_videoid']
        try:
            video = models.Video.objects.get(youtube_videoid=youtube_videoid)
        except models.Video.DoesNotExist:
            video = models.Video(video_type=models.VIDEO_TYPE_YOUTUBE,
                                 youtube_videoid=youtube_videoid,
                                 allow_community_edits=False)
            video.save()
    else:
        video_url = request.GET['video_url']
        try:
            video = models.Video.objects.get(video_url=video_url)
        except models.Video.DoesNotExist:
            video = models.Video(video_type=models.VIDEO_TYPE_HTML5,
                                 video_url=video_url,
                                 allow_community_edits=False)
            video.save()
    null_widget = 'null' in request.GET
    debug_js = 'debug_js' in request.GET
    if 'element_id' in request.GET:
        element_id = request.GET['element_id']
    else:
        element_id = None
    return render_to_response('widget/embed.js', 
                              widget.js_context(request, video, 
                                                null_widget, element_id, 
                                                debug_js),
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

    maybe_add_video_session(request)

    video = models.Video.objects.get(video_id=video_id)
    if video.owner != None and video.owner != request.user:
        return { "can_edit": False, "owned_by" : video.owner.username }
    if not video.can_writelock(request.session[VIDEO_SESSION_KEY]):
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
             "existing" : [caption.to_json_dict() for 
                           caption in existing_captions] }

def start_editing_null(request, video_id):
    if not request.user.is_authenticated():
        captions = []
    else:
        video = models.Video.objects.get(video_id=video_id)
        null_captions = video.null_captions(request.user)
        if null_captions is None:
            captions = []
        else:
            captions = models.VideoCaption.objects.filter(
                null_captions__id__exact = null_captions.id)
    return { 'can_edit': True,
             'version': 0,
             'existing': [caption.to_json_dict() for
                          caption in captions] }

def start_translating(request, video_id, language_code):
    maybe_add_video_session(request)

    video = models.Video.objects.get(video_id=video_id)
    translation_language = video.translation(language_code)
    if translation_language == None:
        translation_language = models.TranslationLanguage(
            video=video,
            language=language_code,
            writelock_session_key='')
        translation_language.save()
    # TODO: note duplication with start_editing. Figure out a way to fix this.
    if not translation_language.can_writelock(
        request.session[VIDEO_SESSION_KEY]):
        return { "can_edit": False, 
                 "locked_by" : video.writelock_owner_name }
    translation_language.writelock(request)
    translation_language.save()
    version_list = list(translation_language.translationversion_set.all())
    if len(version_list) == 0:
        new_version_no = 0
        existing_translations = []
    else:
        max_version = max(version_list, key=lambda v: v.version_no)
        new_version_no = max_version.version_no + 1
        existing_translations = models.Translation.objects.filter(
            version__id__exact = max_version.id)
    return { 'can_edit' : True,
             'version' : new_version_no, 
             'existing' : [trans.to_json_dict() for 
                           trans in existing_translations] }

def start_translating_null(request, video_id, language_code):
    if not request.user.is_authenticated():
        translations = []
    else:
        video = models.Video.objects.get(video_id=video_id)
        null_translations = video.null_translations(request.user, language_code)
        if null_translations is None:
            translations = []
        else:
            translations = models.Translation.objects.filter(
                null_translations__id__exact = null_translations.id)
    return { 'can_edit': True,
             'version': 0,
             'existing': [trans.to_json_dict() for
                          trans in translations] }


def update_video_lock(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    if video.can_writelock(request.session[VIDEO_SESSION_KEY]):
        video.writelock(request)
        video.save()
        return { "response" : "ok" }
    else:
        return { "response" : "failed" }        

def update_video_translation_lock(request, video_id, language_code):
    translation_language = models.Video.objects.get(
        video_id=video_id).translation(language_code)
    if translation_language.can_writelock(request.session[VIDEO_SESSION_KEY]):
        translation_language.writelock(request)
        translation_language.save()
        return { 'response' : 'ok' }
    else:
        return { 'response' : 'failed' }

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
    if not video.can_writelock(request.session[VIDEO_SESSION_KEY]):
        return { "response" : "unlockable" }
    video.writelock(request)
    save_captions_impl(request, video, version_no, deleted, inserted, updated)
    return {"response" : "ok"}

def save_captions_null(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    save_captions_null_impl(request, video, version_no, deleted, inserted, updated)
    return {'response':'ok'}

def save_translations(request, video_id, language_code, version_no, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    translation_language = models.Video.objects.get(
        video_id=video_id).translation(language_code)
    if not translation_language.can_writelock(request.session[VIDEO_SESSION_KEY]):
        return { 'response' : 'unlockable' }
    translation_language.writelock(request)
    save_translations_impl(request, translation_language, 
                           version_no, inserted, updated)
    return {'response':'ok'}

def save_translations_null(request, video_id, language_code, version_no, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    save_translations_null_impl(request, video, language_code, inserted, updated)
    return {'response':'ok'}

def finished_captions(request, video_id, version_no, deleted, inserted, updated):
    video = models.Video.objects.get(video_id=video_id)
    if not video.can_writelock(request.session[VIDEO_SESSION_KEY]):
        return { "response" : "unlockable" }
    last_version = save_captions_impl(request, video, version_no, 
                                      deleted, inserted, updated)
    last_version.is_complete = True
    last_version.save()
    video.release_writelock()
    video.save()
    return { "response" : "ok" }

def finished_captions_null(request, video_id, version_no, deleted, inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    null_captions = save_captions_null_impl(request, video, version_no, 
                                            deleted, inserted, updated)
    null_captions.is_complete = True
    null_captions.save()
    return {'response':'ok'}

def finished_translations(request, video_id, language_code, version_no, 
                          inserted, updated):
    translation_language = models.Video.objects.get(
        video_id=video_id).translation(language_code)
    if not translation_language.can_writelock(request.session[VIDEO_SESSION_KEY]):
        return { 'response' : 'unlockable' }
    last_version = save_translations_impl(request, translation_language,
                                          version_no, inserted, updated)
    last_version.is_complete = True
    last_version.save()
    translation_language.release_writelock()
    translation_language.save()
    video = models.Video.objects.get(video_id=video_id)
    return { 'response' : 'ok',
             'available_languages': 
             [widget.language_to_map(code, LANGUAGES_MAP[code]) for
              code in video.translation_language_codes] }

def finished_translations_null(request, video_id, language_code, version_no, 
                               inserted, updated):
    if not request.user.is_authenticated():
        return { "response" : "not_logged_in" }
    video = models.Video.objects.get(video_id=video_id)
    null_translations = save_translations_null_impl(request, video, language_code, 
                                                    inserted, updated)
    null_translations.is_complete = True
    null_translations.save()
    video = models.Video.objects.get(video_id=video_id)
    return { 'response' : 'ok',
             'available_languages': 
             [widget.language_to_map(code, LANGUAGES_MAP[code]) for
              code in video.null_translation_language_codes(request.user)] }

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return {"respones" : "ok"}

def fetch_SRT(request, video_id, langcode):
    #TODO: handle langcode to generate the SRT of a translation
    captions = fetch_captions(request, video_id)
    srt = [dict_to_srt(index, caption) for index,caption in enumerate(captions)]
    return '\n'.join(srt)

def fetch_captions(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    last_version = video.last_video_caption_version()
    captions = list(last_version.videocaption_set.all())
    return [caption.to_json_dict() for caption in captions]

def fetch_captions_null(request, video_id):
    video = models.Video.objects.get(video_id=video_id)
    null_captions = video.null_captions(request.user)
    captions = list(null_captions.videocaption_set.all())
    return [caption.to_json_dict() for caption in captions]

def fetch_translations(request, video_id, language_code):
    video = models.Video.objects.get(video_id=video_id)
    trans_lang = video.translation(language_code)
    subtitles = list(
        video.last_video_caption_version().videocaption_set.all())
    translations = list(
        trans_lang.last_translation_version().translation_set.all())
    translations_dict = dict([(trans.caption_id, trans) for trans 
                              in translations])
    return [subtitle.to_json_dict(
            None if subtitle.caption_id not in translations_dict
            else translations_dict[subtitle.caption_id].translation_text) 
            for subtitle in subtitles]

def fetch_translations_null(request, video_id, language_code):
    video = models.Video.objects.get(video_id=video_id)
    subtitles = list(video.null_captions(request.user).videocaption_set.all())
    translations = list(video.null_translations(
        request.user, language_code).translation_set.all())
    translations_dict = dict([(trans.caption_id, trans) for 
                              trans in translations])
    return [subtitle.to_json_dict(
            None if subtitle.caption_id not in translations_dict
            else translations_dict[subtitle.caption_id].translation_text) 
            for subtitle in subtitles]    
    

def fetch_captions_and_open_languages(request, video_id):
    return { 'captions': fetch_captions(request, video_id),
             'languages': [widget.language_to_map(lang[0], lang[1]) 
                           for lang in LANGUAGES]}

def fetch_captions_and_open_languages_null(request, video_id):
    return { 'captions': fetch_captions_null(request, video_id),
             'languages': [widget.language_to_map(lang[0], lang[1]) 
                           for lang in LANGUAGES]}

# SRT encoding helpers:
def dict_to_srt(index, caption_dict):
    return str(index+1) + "\n" + encode_srt_time(int(caption_dict["start_time"])) + " --> " + encode_srt_time(int(caption_dict["end_time"])) + "\n" + caption_dict["caption_text"] + "\n"

def encode_srt_helper_toString(val, n):
    result = str(val)
    result = '0'*(n-len(result))+result
    return result

def encode_srt_time(t):
    ms = t%1000
    s = (t/1000)%60
    m = (t/(60*1000))%60
    h = (t/(60*60*1000))%60
    return encode_srt_helper_toString(h,2)+":"+encode_srt_helper_toString(m,2)+":"+encode_srt_helper_toString(s,2)+","+encode_srt_helper_toString(ms,3)

#helpers

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
                                                     user=request.user,
                                                     is_complete=False)
        if last_version != None:
            current_version.is_complete = last_version.is_complete
            current_version.save()
            for caption in list(last_version.videocaption_set.all()):
                current_version.videocaption_set.add(
                    caption.duplicate_for(current_version))
        else:
            current_version.save()
    apply_caption_changes(current_version.videocaption_set, deleted, inserted, 
                          updated, current_version)
    current_version.save()
    return current_version

def save_captions_null_impl(request, video, version_no, deleted, inserted, updated):
    null_captions = video.null_captions(request.user)
    if null_captions is None:
        null_captions = models.NullVideoCaptions(video=video,
                                                 user=request.user)
        null_captions.save()
    apply_caption_changes(null_captions.videocaption_set, deleted, inserted, 
                          updated, None, null_captions)
    null_captions.save()
    return null_captions

def apply_caption_changes(caption_set, deleted, inserted, updated, 
                          version=None, null_captions=None):
    for d in deleted:
        caption_set.remove(caption_set.get(caption_id=d['caption_id']))
    for u in updated:
        caption = caption_set.get(caption_id=u['caption_id'])
        caption.update_from(u)
        caption.save()
    for i in inserted:
        vc = models.VideoCaption(caption_id=i['caption_id'],
                                 caption_text=i['caption_text'],
                                 start_time=i['start_time'],
                                 end_time=i['end_time'])
        if version is not None:
            vc.version = version
        else:
            vc.null_captions = null_captions
        caption_set.add(vc)

def save_translations_impl(request, translation_language,
                           version_no, inserted, updated):
    last_version = translation_language.last_translation_version()
    if last_version != None and last_version.version_no == version_no:
        current_version = last_version
    else:
        current_version = models.TranslationVersion(language=translation_language, 
                                                    version_no=version_no,
                                                    user=request.user,
                                                    is_complete=False)
        if last_version != None:
            current_version.is_complete = last_version.is_complete
            current_version.save()
            for translation in list(last_version.translation_set.all()):
                current_version.translation_set.add(
                    translation.duplicate_for(current_version))
        else:
            current_version.save()
    apply_translation_changes(current_version.translation_set, inserted, 
                              updated, current_version)
    current_version.save()
    return current_version

def save_translations_null_impl(request, video, language_code, inserted, updated):
    null_translations = video.null_translations(request.user, language_code)
    if null_translations is None:
        null_translations = models.NullTranslations(video=video,
                                                    user=request.user,
                                                    language=language_code)
        null_translations.save()
    apply_translation_changes(null_translations.translation_set, inserted, 
                              updated, None, null_translations)
    null_translations.save()
    return null_translations

def apply_translation_changes(translations_set, inserted, updated, 
                              version=None, null_translations=None):
    for u in updated:
        translation = translations_set.get(caption_id=u['caption_id'])
        translation.update_from(u)
        translation.save()
    for i in inserted:
        t = models.Translation(caption_id=i['caption_id'],
                               translation_text=i['text'])
        if version is not None:
            t.version = version
        else:
            t.null_translations = null_translations
        translations_set.add(t)

def maybe_add_video_session(request):
    if VIDEO_SESSION_KEY not in request.session:
        request.session[VIDEO_SESSION_KEY] = str(uuid4()).replace('-', '')
