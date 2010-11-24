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
from django import template
from teams.models import Team, Invite
from videos.models import Action
from django.conf import settings

ACTIONS_ON_PAGE = getattr(settings, 'ACTIONS_ON_PAGE', 10)

register = template.Library()

@register.filter
def can_approve_application(team, user):
    if not user.is_authenticated():
        return False
    return team.can_approve_application(user)

@register.filter
def can_invite_to_team(team, user):
    if not user.is_authenticated():
        return False
    return team.can_invite(user)

@register.filter
def can_add_video_to_team(team, user):
    return team.can_add_video(user)    

@register.filter
def can_edit_video(tv, user):
    return tv.can_edit(user) 

@register.filter
def can_remove_video(tv, user):
    return tv.can_remove(user) 

@register.filter
def is_team_manager(team, user):
    if not user.is_authenticated():
        return False
    return team.is_manager(user)

@register.filter
def is_team_member(team, user):
    if not user.is_authenticated():
        return False
    return team.is_member(user)

@register.inclusion_tag('teams/_team_select.html', takes_context=True)
def team_select(context, team):
    user = context['user']
    qs = Team.objects.exclude(pk=team.pk).filter(users=user)
    return {
        'team': team,
        'objects': qs
    }

@register.inclusion_tag('teams/_team_activity.html', takes_context=True)    
def team_activity(context, team):
    user_ids = team.members.values_list('user__id', flat=True)
    context['membres_actions'] = Action.objects.filter(user__pk__in=user_ids)[:ACTIONS_ON_PAGE]
    
    videos_ids = team.teamvideo_set.values_list('video__id', flat=True)
    context['videos_actions'] = Action.objects.filter(video__pk__in=videos_ids)[:ACTIONS_ON_PAGE]
    
    return context

@register.inclusion_tag('teams/_team_add_video_select.html', takes_context=True)    
def team_add_video_select(context):
    user = context['user']
    if user.is_authenticated():
        qs = Team.objects.filter(users=user)
        context['teams'] = [item for item in qs if item.can_add_video(user)]
    return context 