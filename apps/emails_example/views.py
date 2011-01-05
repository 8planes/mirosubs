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
from videos.models import Video
from django.contrib.sites.models import Site

@check_is_staff
def index(request):
    context = {}
    return direct_to_template(request, 'emails_example/index.html', context)

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
def email_notification(request):
    context = {
        'domain': Site.objects.get_current().domain
    }
    return direct_to_template(request, 'videos/email_notification.html', context)