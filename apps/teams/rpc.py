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
from teams.models import Team, TeamMember, Application
from django.utils.translation import ugettext as _
from utils.rpc import Error, Msg
from utils.rpc import RpcRouter

class TeamsApiClass(object):
    
    def create_application(self, team_id, msg, user):
        if not user.is_authenticated():
            return Error(_('You should be authenticated.'))
            
        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Error(_('Team does not exist'))
        
        try:
            tm = TeamMember.objects.get(team=team, user=user)
            return Error(_(u'You are already a member of this team.'))
        except TeamMember.DoesNotExist:
            pass
        
        if team.is_open():
            TeamMember(team=team, user=user).save()
            return Msg(_(u'You are now a member of this team because it is open.'))
        elif team.is_by_application():
            application, created = Application.objects.get_or_create(team=team, user=user)
            application.note = msg
            application.save()
            return Msg(_(u'Application sent success. Wait for answer from team.'))
        else:
            return Error(_(u'You can\'t join this team by application.'))
        
    def leave(self, team_id, user):
        if not user.is_authenticated():
            return Error(_('You should be authenticated.'))
            
        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Error(_('Team does not exist'))
            
        try:
            tm = TeamMember.objects.get(team=team, user=user)
            if team.members.exclude(pk=tm.pk).exists():
                tm.delete()
                return Msg(_(u'You are not a member of team now.'), is_open=team.is_open())
            else:
                return Error(_(u'You are last member of this team.'))
        except TeamMember.DoesNotExist:
            return Error(_(u'You are not a member of this team.'))
    
    def join(self, team_id, user):
        if not user.is_authenticated():
            return Error(_('You should be authenticated.'))
            
        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Error(_('Team does not exist'))
        
        try:
            TeamMember.objects.get(team=team, user=user)
            return Error(_(u'You are already a member of this team.'))
        except TeamMember.DoesNotExist:
            pass
        
        if not team.is_open():
            return Error(_(u'This team is not open.'))
        else:
            TeamMember(team=team, user=user).save()
            return Msg(_(u'You are now a member of this team.'))

TeamsApi = TeamsApiClass()

rpc_router = RpcRouter('teams:rpc_router', {
    'TeamsApi': TeamsApi
})        