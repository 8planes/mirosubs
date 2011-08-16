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

from django.db import models
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from auth.models import CustomUser as User
from utils import send_templated_email
from localeurl.utils import universal_url
from utils.tasks import send_templated_email_async

from apps.videos.models import SubtitleLanguage, Video
from apps.teams.moderation_const import SUBJECT_EMAIL_VERSION_REJECTED    
COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)
SUBJECT_EMAIL_VIDEO_COMMENTED = "%s left a comment on the video %s"



def notify_comment_by_email(comment,  version=None,  moderator=None, is_rejection=False):
    """
    Comments can be attached to a video (appear in the videos:video (info)) page) OR
                                  sublanguage (appear in the videos:translation_history  page)
    Since version rejection becomes comments for videos we also need to cater for this in the email
                                  
    """
    ct = comment.content_object
    if isinstance( ct, Video):
        video = ct
        version = None
        language = None
    elif isinstance(ct, SubtitleLanguage ):
        video = ct.video
        language = ct

    domain = Site.objects.get_current().domain
    email_body = render_to_string("comments/email/comment-notification.html", {
            "video": video,
            "version": version,
            "moderator": moderator,
            "domain":domain,
            "body": comment.content,
            "language":language,
            "is_rejection":is_rejection,
            })
    if language:
        language_url = universal_url("videos:translation_history", kwargs={
            "video_id": video.video_id,
            "lang": language.language,
            "lang_id": language.pk,
        })
    else:
        language_url = None
    if version:
        version_url = universal_url("videos:revision", kwargs={
            "pk": version.pk,
        })
    else:
        version_url = None
    user = moderator or comment.user    
    user_url = universal_url("profiles:profile", args=(user.id,))
    
    if is_rejection:
        subject = SUBJECT_EMAIL_VERSION_REJECTED  % video.title_display()
    else:
        subject = SUBJECT_EMAIL_VIDEO_COMMENTED  % (comment.user.username, video.title_display())

    followers = set(video.notification_list(comment.user))
    if language:
        followers.update(language.notification_list(comment.user))
    for user in followers:
        send_templated_email_async.delay(
            user.email,
            subject,
            "comments/email/comment-notification.html", {
                "version": version,
                "moderator": moderator,
                "version_url":version_url,
                "language_url":language_url,
                "domain":domain,
                "version": version,
            }, not settings.DEBUG)

