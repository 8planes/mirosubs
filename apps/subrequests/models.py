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

from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from auth.models import CustomUser as User
from videos.models import Video, Action, ALL_LANGUAGES

class SubtitleRequestManager(models.Manager):
    '''
    Custom manager for subtitle requests. Provides methods for creation
    of requests from provided video, user and languages.
    '''

    def _create_request(self, video, user, language, action, track=True,
                        description=''):
        '''
        Create a subtitle request for single language.
        '''

        subreq, new = self.get_or_create(user=user, video=video,
                                         language=language, track=track,
                                         description=description)
        if not new:
            # Mark as 'not done' as it is reopened.
            subreq.done = False
            subreq.reopened = True
            subreq.save()

        subreq.actions.add(action)
        return subreq

    def create_requests(self, video_id, user, languages, track=True,
                        description=''):
        '''
        Create multiple requests according to the list of languages provided.
        '''

        video = Video.objects.get(video_id=video_id)
        subreqs = []

        # A new action relating the requested sub langs
        action = Action.objects.create(
            user=user,
            video=video,
            action_type=Action.SUBTITLE_REQUEST,
            created=datetime.now(),
        )

        for language in languages:
            subreqs.append(self._create_request(video, user, language,
                                                action, track))
        return subreqs

class SubtitleRequest(models.Model):
    '''
    A request for subtitles.
    '''
    video = models.ForeignKey(Video)
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES)
    user = models.ForeignKey(User, related_name='subtitlerequests')
    done = models.BooleanField(_('request completed'))
    reopened = models.BooleanField(_('request has been reopened'))
    actions = models.ManyToManyField(Action, related_name='subtitlerequests',
                                     blank=True, null=True)
    track = models.BooleanField(_('follow related activities'), default=True)
    description = models.TextField(_('description of the request'), blank=True)
    objects = SubtitleRequestManager()

    def __unicode__(self):
        return "%s-%s request (%s)" %(self.video, self.get_language_display(),
                                       self.user)

    class Meta:
        unique_together = ('video', 'user', 'language')
