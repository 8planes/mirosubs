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

from videos.models import Video
from piston.handler import BaseHandler
from piston.utils import rc, validate
from django.contrib.sites.models import Site
from forms import GetVideoForm

class VideoHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('title', 'description', 'video_id', 'thumbnail', 'created', 
              'allow_community_edits', 'allow_video_urls_edit', 'homepage')
    
    @classmethod
    def thumbnail(self, obj):
        return obj.get_thumbnail()
    
    @classmethod
    def homepage(self, obj):
        site = Site.objects.get_current()
        return 'http://%s%s' % (site.domain, obj.get_absolute_url())
    
    @validate(GetVideoForm, 'GET')    
    def read(self, request, video_id=None):
        video = None
        
        if video_id:
            try:
                video = Video.objects.get(video_id=video_id)
            except Video.DoesNotExist:
                pass
        else:
            video = request.form.save()
            
        if not video:
            return rc.NOT_FOUND
        else:
            return video