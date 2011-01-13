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

from django.views.generic.simple import direct_to_template
from utils import check_is_staff
from videos.models import Video, SubtitleLanguage
from django.contrib.sites.models import Site
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@check_is_staff
def index(request):
    context = {}
    return direct_to_template(request, 'emails_example/index.html', context)

@check_is_staff
def send_email(request):
    email = request.POST.get('email', '')
    subject = request.POST.get('subject', '')
    type = request.POST.get('type', '')

    if not email or not subject or not type:
        messages.error(request, u'Email or subject or email type is undefined.')
    else:
        try:
            validate_email(email)
        except ValidationError:
            email = None
            messages.error(request, u'Invalid email.')
        
    if type == '1':
        content = email_title_changed(request).content
    elif type == '2':
        content = email_start_notification(request).content
    elif type == '3':
        content = email_video_url_add(request).content        
    else:
        content = None
        messages.error(request, u'Undefined type')
    
    if content and email and subject:
        email = EmailMessage(subject, content, to=[email])
        email.content_subtype = 'html'
        email.send()
        
    return redirect('emails_example:index')       
    
@check_is_staff
def email_title_changed(request):
    try:
        video = Video.objects.exclude(title__isnull=True).exclude(title='')[:1].get()
    except Video.DoesNotExist:
        video = None
        
    context = {
        'old_title': u'Old title',
        'editor': request.user,
        'video': video,
        'domain': Site.objects.get_current().domain
    }
    return direct_to_template(request, 'videos/email_title_changed.html', context)

@check_is_staff
def email_video_url_add(request):
    try:
        video = Video.objects.exclude(Q(videourl__isnull=True)|Q(videourl__added_by__isnull=True))[:1].get()
        video_url = video.videourl_set.exclude(added_by__isnull=True)[:1].get()
    except Video.DoesNotExist:
        video = None    
        video_url = None
        
    context = {
        'video': video,
        'video_url': video_url,
        'domain': Site.objects.get_current().domain
    }
    return direct_to_template(request, 'videos/email_video_url_add.html', context)

@check_is_staff
def email_start_notification(request):
    try:
        language = SubtitleLanguage.objects.all()[:1].get()
    except SubtitleLanguage.DoesNotExist:
        language = None

    context = {
        'domain': Site.objects.get_current().domain,
        'language': language,
        'version': {'user': request.user},
        'video': language.video
    }
    return direct_to_template(request, 'videos/email_start_notification.html', context)