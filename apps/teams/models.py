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
from videos.models import Video
from auth.models import CustomUser as User
from sorl.thumbnail.main import DjangoThumbnail

class TeamManager(models.Manager):
    
    def for_user(self, user):
        if user.is_authenticated():
            return self.get_query_set().filter(models.Q(is_visible=True)| \
                                        models.Q(members__user=user)).distinct()
        else:
            return self.get_query_set().filter(is_visible=True)
    
class Team(models.Model):
    APPLICATION = 1
    INVITATION_BY_MANAGER = 2
    INVITATION_BY_ALL = 3
    OPEN = 4
    MEMBERSHIP_POLICY_CHOICES = (
        (APPLICATION, _(u'Application')),
        (INVITATION_BY_MANAGER, _(u'Invitation by manager')),
        (INVITATION_BY_ALL, _(u'Invitation by any member')),
        (OPEN, _(u'Open')),
    )
    MEMBER_REMOVE = 1
    MANAGER_REMOVE = 2
    MEMBER_ADD = 3
    VIDEO_POLICY_CHOICES = (
        (MEMBER_REMOVE, _(u'Members add/remove')),
        (MANAGER_REMOVE, _(u'Managers add/remove')),
        (MEMBER_ADD, _(u'Members add videos'))
    )
    
    name = models.CharField(_(u'name'), max_length=250, unique=True)
    description = models.TextField(_(u'description'), blank=True)
    logo = models.ImageField(_(u'logo'), upload_to='teams/logo/', blank=True)
    membership_policy = models.IntegerField(_(u'membership policy'), choices=MEMBERSHIP_POLICY_CHOICES)
    video_policy = models.IntegerField(_(u'video policy'), choices=VIDEO_POLICY_CHOICES)
    is_visible = models.BooleanField(_(u'is public visible'), default=True)
    videos = models.ManyToManyField(Video, blank=True, verbose_name=_('videos'))
    users = models.ManyToManyField(User, through='TeamMember', related_name='teams', verbose_name=_('users'))
    points = models.IntegerField(default=0, editable=False)
    applicants = models.ManyToManyField(User, through='Application', related_name='applicated_teams', verbose_name=_('applicants'))
    invited = models.ManyToManyField(User, through='Invite', verbose_name=_('invited'))
    
    objects = TeamManager()
    
    class Meta:
        ordering = ['-name']
        verbose_name = _(u'Team')
        verbose_name_plural = _(u'Teams')
    
    def __unicode__(self):
        return self.name
    
    def logo_thumbnail(self):
        if self.logo:
            return DjangoThumbnail(self.logo, (128, 128), opts={'crop': 'smart'})
    
    @models.permalink
    def get_absolute_url(self):
        return ('teams:detail', [self.pk])
    
    @models.permalink
    def get_edit_url(self):
        return ('teams:edit', [self.pk])
    
    def is_manager(self, user):
        return self.members.filter(user=user, is_manager=True).exists()
    
    def is_member(self, user):
        return self.members.filter(user=user).exists()
    
    def can_remove_video(self, user):
        if self.video_policy == self.MANAGER_REMOVE and self.is_manager(user):
            return True
        if self.video_policy == self.MEMBER_REMOVE and self.is_member(user):
            return True
        return False
    
    def can_add_video(self, user):
        if self.video_policy == self.MANAGER_REMOVE and self.is_manager(user):
            return True
        if self.is_member(user):
            return True
        return False
    
class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name='members')
    user = models.ForeignKey(User)
    is_manager = models.BooleanField(default=False)
    
class Application(models.Model):
    team = models.ForeignKey(Team, related_name='applications')
    user = models.ForeignKey(User, related_name='team_applications')
    note = models.TextField(blank=True)
    
class Invite(models.Model):
    team = models.ForeignKey(Team, related_name='invitations')
    user = models.ForeignKey(User, related_name='team_invitations')
    note = models.TextField(blank=True)