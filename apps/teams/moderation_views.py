import json

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse, Http404
from django.views.decorators.http import  require_POST
from django.template import RequestContext
from django.utils.functional import  wraps

from django.views.generic.list_detail import object_list

from utils.translation import get_user_languages_from_request, get_languages_list

from apps.teams.moderation import CAN_MODERATE_VERSION, CAN_SET_VIDEO_AS_MODERATED,\
  CAN_UNSET_VIDEO_AS_MODERATED, MODERATION_STATUSES, UNMODERATED, APPROVED, \
  WAITING_MODERATION, REJECTED
from apps.teams.templatetags.moderation import render_moderation_togggle_button, render_moderation_icon

from apps.videos.models import SubtitleVersion
from apps.teams.models import Team, TeamVideo
from apps.teams.moderation_forms import ModerationListSearchForm
from haystack.query import SearchQuerySet

from apps.teams.moderation import _update_search_index

from utils.jsonresponse import to_json

def _check_moderate_permission(view):
    def wrapper(request,  *args, **kwargs):

        team = Team.objects.get(pk=kwargs.pop("team_id", "-1"))
        if not team.is_member(request.user):
            return  HttpResponseForbidden("This user does not have the permission to moderate this team")
        return view(request, team, *args, **kwargs)
    return wraps(view)(wrapper)

def _set_moderation(request, team, version, status,  updates_meta=True):
    try:
        if not isinstance(version, SubtitleVersion):
            version = get_object_or_404(SubtitleVersion, pk=version)
        if not isinstance(team, Team):
            team = get_object_or_404(Team, pk=team)


        if status == APPROVED:
            approve_version(version, team, request.user, updates_meta)
        elif status == REJECTED:
            reject_version(version, team, request.user, updates_meta)
        if request.is_ajax():
            return {
                        "status":"ok",
                        "status_icon_html": render_moderation_icon(version),
                        "new_button_html":render_moderation_togggle_button(version)}
        else:
            return HttpResponseRedirect(reverse("videos:revision", kwargs={'pk':version.pk}))
    except SuspiciousOperation:
        error_message = "User cannot approve  this video"
        if request.is_ajax():
            return HttpResponse(json.dumps({"success":False, "message": error_message}))
        return HttpResponseForbidden(error_message)
        
@to_json    
@_check_moderate_permission
@require_POST
def approve_version(request, team, version_id):
    res =  _set_moderation(request, team, version_id, APPROVED)
    res['msg'] = "Version approved, well done!"

@to_json
@_check_moderate_permission
@require_POST
def reject_version(request, team, version_id):
    rejection_message = None
    if request.POST.get("message"):
        # we should send the user a message
        rejection_message = request.POST.get("message")
    res =  _set_moderation(request, team, version_id, REJECTED, rejection_message=rejection_message)
    res['msg'] = "Version rejected!"
    return res

@to_json
@_check_moderate_permission
@require_POST
def remove_moderation_version(request, team, version_id):
    return _set_moderation(request, team, version_id, WAITING_MODERATION, msg="Moderation data deleted")

def _batch_set_moderation(request, team, status, before_rev=None, lang_id= None):
    if before_rev is not None:
        versions = team.get_pending_moderation().filter(pk__lte=before_rev, language=lang_id)
    else:    
        versions = request.POST.get("version_ids" , None)
    res = []
    versions = list(versions)
    for v in versions:
        _set_moderation(request, team, v, APPROVED,  updates_meta=False)
    if len(versions):
        _update_search_index(versions[0].video)
        language_id = versions[0].language.pk
    else:
        language_id = None
    return  {
        "lang_id":language_id,
        "count": len(versions),
        "pending_count" : team.get_pending_moderation().count(),
        "msg":"Moderation statuses approved",
    }

@to_json
@_check_moderate_permission
@require_POST
def batch_approve_version(request, team, before_rev=None, lang_id=None):
    s = _batch_set_moderation(request, team, APPROVED, before_rev, lang_id)
    s["msg"] = "Subs approved."
    return s

@to_json
@_check_moderate_permission
@require_POST
def batch_reject_version(request, team, before_rev=None, lang_id=None):
    s = _batch_set_moderation(request, team, REJECTED, before_rev, lang_id)
    s["msg"] = "Subs rejected."
    return s

def _get_moderation_results(request, team):
    sqs = SearchQuerySet().models(TeamVideo).filter(needs_moderation=True)
    form = ModerationListSearchForm(request)
    result_list = []
    if form.is_valid():
        result_list = form.search_qs(sqs)
    return form, result_list

@_check_moderate_permission
@require_POST
def get_pending_videos(request, team):
    form, result_list = _get_moderation_results(request, team)
    return render_to_response('moderation/_videos_to_moderate.html', {
            'team': team,
            "form":form,
            "result_list":result_list
             }, RequestContext(request))
    return

@_check_moderate_permission
def edit_moderation(request, team ):
    form, result_list = _get_moderation_results(request, team)
    return render_to_response('moderation/dashboard.html', {
            'team': team,
            "form":form,
            "result_list":result_list
             }, RequestContext(request))

@to_json
@_check_moderate_permission
@require_POST
def affect_selected(request, team):
    if request.method == "POST":
        action = request.POST.get("action", False)
        ids = request.POST.get("ids", "").split("-")
        lang_ids = request.POST.get("lang_ids", "").split("-")
        if action in [APPROVED , REJECTED]:
            for version_id, lang_id in zip(ids, lang_ids):
                 _batch_set_moderation(request, team, action, version_id, lang_id)
            res = {}
            res["pending_count"] = team.get_pending_moderation().count()
            res["msg"] = "Subs moderated"
            return res                    
                    
