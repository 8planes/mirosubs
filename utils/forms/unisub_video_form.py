
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

from utils.forms import UniSubURLField
from urlparse import urlparse
from django.contrib.sites.models import Site
from localeurl.utils import strip_path
from django.core.urlresolvers import resolve
from django import forms
from videos.models import Video
from django.http import Http404
from videos.types import VideoTypeError
from django.utils.safestring import mark_safe
from django.conf import settings
from videos.types import video_type_registrar
from django.utils.translation import ugettext_lazy as _

class UniSubBoundVideoField(UniSubURLField):
    def format_url(self, url):
        parsed_url = urlparse(url)
        return '%s://%s%s' % (parsed_url.scheme or 'http', parsed_url.netloc, parsed_url.path)  
    
    def clean(self, value):
        super(UniSubBoundVideoField, self).clean(value)
        self.vt = None    
        self.video = None
        video_url = value
        
        if not video_url:
            return video_url

        host = Site.objects.get_current().domain
        url_start = 'http://'+host
        
        if video_url.startswith(url_start):
            #UniSub URL
            locale, path = strip_path(video_url[len(url_start):])
            video_url = url_start+path
            try:
                video_url = self.format_url(video_url)
                func, args, kwargs = resolve(video_url.replace(url_start, ''))
                
                if not 'video_id' in kwargs:
                    raise forms.ValidationError(_('This URL does not contain video id.'))
                
                try:
                    self.video = Video.objects.get(video_id=kwargs['video_id'])
                except Video.DoesNotExist:
                    raise forms.ValidationError(_('Videos does not exist.'))
                
            except Http404:
                raise forms.ValidationError(_('Incorrect URL.'))
        else:
            #URL from other site
            try:
                self.vt = video_type_registrar.video_type_for_url(video_url)
                
                if hasattr(self, 'user'):
                    user = self.user
                else:
                    user = None

                if self.vt:
                    self.video, created = Video.get_or_create_for_url(vt=self.vt, user=user)
            except VideoTypeError, e:
                self.video = None
                raise forms.ValidationError(e)

            if not self.video:
                raise forms.ValidationError(mark_safe(_(u"""Universal Subtitles does not support that website or video format.
If you'd like to us to add support for a new site or format, or if you
think there's been some mistake, <a
href="mailto:%s">contact us</a>!""") % settings.FEEDBACK_EMAIL))
             
        return video_url        