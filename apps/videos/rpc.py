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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from videos.models import Video, SubtitleLanguage
from django.utils.translation import ugettext as _

class VideosApiClass(object):
    
    def follow(self, video_id, user):
        if not user.is_authenticated():
            return dict(error=_(u'You should be authenticated.'))
        
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return dict(error=_(u'Video does not exist.'))
        
        video.followers.add(user)
        
        for l in video.subtitlelanguage_set.all():
            l.followers.add(user)   
        
        return dict(msg=_(u'You are following this video now.'))
    
    def unfollow(self, video_id, user):
        if not user.is_authenticated():
            return dict(error=_(u'You should be authenticated.'))
        
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return dict(error=_(u'Video does not exist.'))
        
        video.followers.remove(user)
        
        for l in video.subtitlelanguage_set.all():
            l.followers.remove(user)        
        
        return dict(msg=_(u'You stopped following this video now.'))
    
    def follow_language(self, language_id, user):
        if not user.is_authenticated():
            return dict(error=_(u'You should be authenticated.'))
        
        try:
            language = SubtitleLanguage.objects.get(pk=language_id)
        except SubtitleLanguage.DoesNotExist:
            return dict(error=_(u'Subtitles does not exist.'))
        
        language.followers.add(user)
        
        return dict(msg=_(u'You are following this subtitles now.'))
    
    def unfollow_language(self, language_id, user):
        if not user.is_authenticated():
            return dict(error=_(u'You should be authenticated.'))
        
        try:
            language = SubtitleLanguage.objects.get(pk=language_id)
        except SubtitleLanguage.DoesNotExist:
            return dict(error=_(u'Subtitles does not exist.'))
        
        language.followers.remove(user)
        
        return dict(msg=_(u'You stopped following this subtitles now.'))