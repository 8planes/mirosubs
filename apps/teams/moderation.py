from apps.teams.moderation_const import *

import datetime

from django.db import models
from django.core.exceptions import SuspiciousOperation
from django.contrib.sites.models import Site

from haystack import site

from utils.db import require_lock
from utils.tasks import send_templated_email_async

from apps.videos.models import Video, SubtitleVersion, SubtitleLanguage, Action
from apps.teams.models import TeamVideo

from apps.auth.models import CustomUser as User
from apps.comments.notifications import notify_comment_by_email
from widget.rpc import video_cache


def _update_search_index(video):
    if video.moderated_by:
        tv = TeamVideo.objects.get(video=video, team=video.moderated_by)
        site.get_index(TeamVideo).update_object(tv)

class AlreadyModeratedException(Exception):
    pass

def user_can_moderate(video, user):
    if not user.is_authenticated():
        return False
    return video.moderated_by and video.moderated_by.is_contributor(user)

def is_moderated(version_lang_or_video):
    if isinstance(version_lang_or_video , SubtitleVersion):
        return version_lang_or_video.moderation_status != UNMODERATED
    elif isinstance(version_lang_or_video, SubtitleLanguage):
        video = version_lang_or_video.video
    elif isinstance(version_lang_or_video, Video):
        video = version_lang_or_video
    return bool(video.moderated_by)


#@require_lock
def add_moderation( video, team, user):
    """
    Adds moderation and approves all 
    """
    if video.moderated_by :
        raise AlreadyModeratedException("Video is already moderated")
    if not team.can_add_moderation(user) :       
        raise SuspiciousOperation("User cannot set this video as moderated")
    video.moderated_by = team
    video.save()
    SubtitleVersion.objects.filter(language__video__id = video.pk, moderation_status=UNMODERATED).update(moderation_status=APPROVED)
    video_cache.invalidate_cache(video.video_id)
    _update_search_index(video)
    return True


#@require_lock
def remove_moderation( video,  team, user):
    """
    Removes the moderation lock for that video, sets all the sub versions to
    approved , invalidates the cache and updates the search index.
    """
    if not video.moderated_by:
        return None
    if not team.can_remove_moderation( user) :       
        raise SuspiciousOperation("User cannot unset this video as moderated")
    for lang in video.subtitlelanguage_set.all():
        latest = lang.latest_version(public_only=False)
        if latest and latest.moderation_status == REJECTED:
            # rollback to the last moderated status
            latest_approved = lang.latest_version(public_only=Tue)
            v = latest_approved.rollback(user)
            v.save()
        
    num = SubtitleVersion.objects.filter(language__video=video).update(moderation_status=UNMODERATED)
    video.moderated_by = None;
    video.save()
    video_cache.invalidate_cache(video.video_id)
    _update_search_index(video)
    return num

def _set_version_moderation_status(version, team, user, status, updates_meta=True):
    if not user_can_moderate(version.language.video, user):
        raise SuspiciousOperation("User cannot approve this version")    
    version.moderation_status = status
    version.save()
    if updates_meta:
        video_cache.invalidate_cache(version.video.video_id)
        _update_search_index(version.video)
    return version    

def approve_version( version, team, user, updates_meta=True):
    res =  _set_version_moderation_status(version, team, user, APPROVED, updates_meta)
    Action.create_approved_video_handler(version, user)

def reject_version(version, team, user, rejection_message=None, sender=None, updates_meta=True, ):
    v = _set_version_moderation_status(version, team, user, REJECTED, updates_meta)

    latest = version.language.latest_version(public_only=False)
    if latest and latest.moderation_status == REJECTED:
        # rollback to the last moderated status
        latest_approved = version.language.latest_version(public_only=True)
        if latest_approved:
            latest_approved.rollback(user)
    if bool(rejection_message) and bool(sender):
        comment = create_comment_for_rejection(version, rejection_message, sender)
        notify_comment_by_email(comment, version.language, moderator = sender, is_rejection=True )
    return v

def create_comment_for_rejection(version, msg, sender):
    from apps.comments.models import Comment
    comment = Comment(content_object=version.language,
                      user = sender,
                      content = msg,
                      submit_date = datetime.datetime.now()
    )
    comment.save()
    return comment
    


