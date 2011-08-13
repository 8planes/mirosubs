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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from auth.models import CustomUser as User
from videos.models import Video, Action, SubtitleLanguage, ALL_LANGUAGES

class SubtitleRequestManager(models.Manager):
    '''
    Custom manager for subtitle requests. Provides methods for creation
    of requests from provided video, user and languages.
    '''

    def _create_request(self, video, user, language, track=True,
                        description=''):
        '''
        Create a subtitle request for single language.
        '''

        subreq, new = self.get_or_create(user=user, video=video,
                                         language=language, track=track,
                                         description=description, done=False)

        # Mark all other requests with same video, user, language triad as done
        self.filter(user=user, video=video, language=language) \
            .exclude(pk=subreq.pk).update(done=True)

        subtitle_language = subreq.subtitle_language()
        if subtitle_language:
            if track:
                subtitle_language.followers.add(user)
            subtitle_language.is_complete = False
            subtitle_language.save()

        return subreq

    def create_requests(self, video_id, user, languages, track=True,
                        description=''):
        '''
        Create multiple requests according to the list of languages provided.
        '''

        video = Video.objects.get(video_id=video_id)
        subreqs = []

        for language in languages:
            subreqs.append(self._create_request(video, user, language, track,
                                                description))
        return subreqs  # self.filter(id__in=subreqs)

class SubtitleRequest(models.Model):
    '''
    A request for subtitles.
    '''
    video = models.ForeignKey(Video)
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES)
    user = models.ForeignKey(User)
    done = models.BooleanField(_('request completed'))
    action = models.ForeignKey(Action, blank=True, null=True)
    track = models.BooleanField(_('follow related activities'), default=True)
    description = models.TextField(_('description of the request'), blank=True)
    objects = SubtitleRequestManager()

    def __unicode__(self):
        return "%s-%s request (%s)" %(self.video, self.get_language_display(),
                                       self.user)

    def subtitle_language(self):
        '''
        The subtitle language which is related to this subtitle request.
        '''
        return self.video.subtitle_language(self.language)

    @classmethod
    def subtitlelanguage_handler(cls, sender, instance, created, **kwargs):
        related_requests = cls.objects.filter(
            language=instance.language,
            #done=False
        )

        if related_requests:

            if created:
                # Adds followers to languages which have pending requests and
                # were not already existing.
                tracked_requests = related_requests.filter(track=True)
                for user in tracked_requests.values_list('user', flat=True):
                    instance.followers.add(user)

            elif instance.is_complete:
                # Marks request as completed according to subtitle status.
                related_requests.update(done=True)

models.signals.post_save.connect(Action.create_subrequest_handler,
                                 SubtitleRequest)

models.signals.post_save.connect(SubtitleRequest.subtitlelanguage_handler,
                                 SubtitleLanguage)
