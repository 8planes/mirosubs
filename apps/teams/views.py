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
from utils import render_to, render_to_json
from teams.forms import CreateTeamForm, EditTeamForm
from teams.models import Team, TeamMember
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from django.views.generic.list_detail import object_list
from videos.models import Video
from auth.models import CustomUser as User

TEAMS_ON_PAGE = getattr(settings, 'TEAMS_ON_PAGE', 12)

def index(request):
    qs = Team.objects.for_user(request.user)
    extra_context = {}
    return object_list(request, queryset=qs,
                       paginate_by=TEAMS_ON_PAGE,
                       template_name='teams/index.html',
                       template_object_name='teams',
                       extra_context=extra_context)

@render_to('teams/detail.html')
def detail(request, pk):
    team = get_object_or_404(Team.objects.for_user(request.user), pk=pk)
    return {
        'team': team
    }

@render_to('teams/create.html')
@login_required    
def create(request):
    if request.method == 'POST':
        form = CreateTeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(request.user)
            messages.success(request, _('Team created success'))
            return redirect(team.get_edit_url())
    else:
        form = CreateTeamForm()
    return {
        'form': form
    }

@render_to('teams/edit.html')
@login_required
def edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    
    if not team.is_member(request.user):
        raise Http404
    
    if not team.is_manager(request.user):
        return {
            'team': team
        }
    
    if request.method == 'POST':
        form = EditTeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, _('Team edited success'))
            return redirect(team.get_edit_url())
    else:
        form = EditTeamForm(instance=team)
    return {
        'form': form,
        'team': team
    }

@login_required
def edit_video(request, pk):
    team = get_object_or_404(Team, pk=pk)

    if not team.is_member(request.user):
        raise Http404
    
    qs = team.videos.all()
    
    extra_context = {
        'team': team,
        'can_remove_video': team.can_remove_video(request.user)
    }
    return object_list(request, queryset=qs,
                       paginate_by=3,
                       template_name='teams/edit_video.html',
                       template_object_name='videos',
                       extra_context=extra_context)

@render_to_json
@login_required    
def remove_video(request, pk, video_pk):
    team = get_object_or_404(Team, pk=pk)

    if not team.is_member(request.user):
        raise Http404
    
    if team.can_remove_video(request.user):
        video = get_object_or_404(Video, pk=video_pk)
        team.videos.remove(video)
        return {
            'success': True
        }        
    else:
        return {
            'success': False,
            'error': ugettext('You can\'t remove video')
        }
        
@render_to_json
@login_required
def remove_member(request, pk, user_pk):
    team = get_object_or_404(Team, pk=pk)

    if not team.is_member(request.user):
        raise Http404

    if team.is_manager(request.user):
        user = get_object_or_404(User, pk=user_pk)
        if not user == request.user:
            TeamMember.objects.filter(team=team, user=user).delete()
            return {
                'success': True
            }
        else:
            return {
                'success': False,
                'error': ugettext('You can\'t remove youself')
            }          
    else:
        return {
            'success': False,
            'error': ugettext('You can\'t remove user')
        }        

@login_required
def demote_member(request, pk, user_pk):
    team = get_object_or_404(Team, pk=pk)

    if not team.is_member(request.user):
        raise Http404

    if team.is_manager(request.user):
        user = get_object_or_404(User, pk=user_pk)
        if not user == request.user:
            TeamMember.objects.filter(team=team, user=user).update(is_manager=False)
        else:
            messages.error(request, _('You can\'t demote to member yorself'))
    else:
        messages.error(request, _('You can\'t demote to member'))          
    return redirect('teams:edit_members', team.pk)

@login_required
def promote_member(request, pk, user_pk):
    team = get_object_or_404(Team, pk=pk)

    if not team.is_member(request.user):
        raise Http404

    if team.is_manager(request.user):
        user = get_object_or_404(User, pk=user_pk)
        if not user == request.user:
            TeamMember.objects.filter(team=team, user=user).update(is_manager=True)
    else:
        messages.error(request, _('You can\'t promote to manager'))
    return redirect('teams:edit_members', team.pk)

@login_required        
def edit_members(request, pk):
    team = get_object_or_404(Team, pk=pk)
    
    if not team.is_member(request.user):
        raise Http404
        
    qs = team.members.select_related()
    
    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    
    if ordering == 'username' and order_type in ['asc', 'desc']:
        pr = '-' if order_type == 'desc' else ''
        qs = qs.order_by(pr+'user__first_name', pr+'user__last_name', pr+'user__username')
    elif ordering == 'role' and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+'is_manager')
    extra_context = {
        'team': team,
        'ordering': ordering,
        'order_type': order_type
    }
    return object_list(request, queryset=qs,
                       paginate_by=50,
                       template_name='teams/edit_members.html',
                       template_object_name='members',
                       extra_context=extra_context)    

@render_to('teams/aplications.html')
@login_required
def aplications(request, pk):
    team = get_object_or_404(Team, pk=pk)
    
    if not team.is_member(request.user):
        raise Http404
        
    return {
        'team': team
    }    