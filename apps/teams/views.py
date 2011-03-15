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
from teams.forms import CreateTeamForm, EditTeamForm, EditTeamFormAdmin, AddTeamVideoForm, EditTeamVideoForm, EditLogoForm
from teams.models import Team, TeamMember, Invite, Application, TeamVideo
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from django.views.generic.list_detail import object_list
from auth.models import CustomUser as User
from django.db.models import Q, Count
from django.contrib.auth.decorators import permission_required
import random
from widget.views import base_widget_params
import widget
from videos.models import Action, SubtitleLanguage, WRITELOCK_EXPIRATION
from django.utils import simplejson as json
from utils.amazon import S3StorageError
from utils.translation import get_user_languages_from_request
from utils.multy_query_set import MultyQuerySet, TeamMultyQuerySet
from teams.rpc import TeamsApi
import datetime

TEAMS_ON_PAGE = getattr(settings, 'TEAMS_ON_PAGE', 12)
HIGHTLIGHTED_TEAMS_ON_PAGE = getattr(settings, 'HIGHTLIGHTED_TEAMS_ON_PAGE', 10)
VIDEOS_ON_PAGE = getattr(settings, 'VIDEOS_ON_PAGE', 30) 
MEMBERS_ON_PAGE = getattr(settings, 'MEMBERS_ON_PAGE', 30)
APLICATIONS_ON_PAGE = getattr(settings, 'APLICATIONS_ON_PAGE', 30)
ACTIONS_ON_PAGE = getattr(settings, 'ACTIONS_ON_PAGE', 20)
DEV = getattr(settings, 'DEV', False)
DEV_OR_STAGING = DEV or getattr(settings, 'STAGING', False)

def index(request, my_teams=False):
    q = request.REQUEST.get('q')
    
    ordering = request.GET.get('o', 'name')

    if my_teams and request.user.is_authenticated():
        qs = Team.objects.filter(members__user=request.user)
    else:
        qs = Team.objects.for_user(request.user).annotate(_member_count=Count('users__pk'))
    
    if q:
        qs = qs.filter(Q(name__icontains=q)|Q(description__icontains=q))
    
    order_fields = {
        'name': 'name',
        'date': 'created',
        'members': '_member_count'
    }
    order_fields_name = {
        'name': _(u'Name'),
        'date': _(u'Newest'),
        'members': _(u'Most Members')
    }
    order_fields_type = {
        'name': 'asc',
        'date': 'desc',
        'members': 'desc'
    }    
    order_type = request.GET.get('ot', order_fields_type.get(ordering, 'desc'))

    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
    
    highlighted_ids = list(Team.objects.filter(highlight=True).values_list('id', flat=True))
    random.shuffle(highlighted_ids)
    highlighted_qs = Team.objects.filter(pk__in=highlighted_ids[:HIGHTLIGHTED_TEAMS_ON_PAGE]) \
        .annotate(_member_count=Count('users__pk'))
    
    extra_context = {
        'my_teams': my_teams,
        'query': q,
        'ordering': ordering,
        'order_type': order_type,
        'order_name': order_fields_name.get(ordering, 'name'),
        'highlighted_qs': highlighted_qs,
        'can_create_team': DEV or (request.user.is_superuser and request.user.is_active)
    }
    return object_list(request, queryset=qs,
                       paginate_by=TEAMS_ON_PAGE,
                       template_name='teams/index.html',
                       template_object_name='teams',
                       extra_context=extra_context)
    
def detail(request, slug):
    from utils.templatetags.optimization import print_query_count
    
    team = Team.get(slug, request.user)
    
    languages = get_user_languages_from_request(request)
    languages.extend([l[:l.find('-')] for l in languages if l.find('-') > -1])
    languages.append('')
    video_ids = team.teamvideo_set.values_list('video_id', flat=True)

    writelock_cutoff = datetime.datetime.now() - datetime.timedelta(seconds=WRITELOCK_EXPIRATION)

    qs = SubtitleLanguage.objects.filter(video__in=video_ids).filter(language__in=languages) \
        .exclude(writelock_time__gte=writelock_cutoff) \
        .filter(video__subtitlelanguage__language__in=languages) \
        .extra(where=['NOT ((SELECT vsl.has_version FROM videos_subtitlelanguage AS vsl WHERE vsl.is_original = %s AND vsl.video_id = videos_subtitlelanguage.video_id) = %s AND videos_subtitlelanguage.is_original=%s)'], params=(True, False, False,)) \
        .distinct()
        
    # all videos not in the list
    _sl_videos_ids = qs.values_list('video_id', flat=True)
    complement_video_ids = [id for id in video_ids if id not in _sl_videos_ids]
    qs_complement = SubtitleLanguage.objects.filter(video__in=complement_video_ids).filter(is_original=True)
    
    qs1 = qs.filter(is_forked=False, is_original=False).filter(percent_done__lt=100, percent_done__gt=0)
    qs2 = qs.filter(is_forked=False, is_original=False).filter(percent_done=0)
    qs3 = qs.filter(is_original=True).filter(subtitleversion__isnull=True)
    qs4 = qs.filter(is_forked=False, is_original=False).filter(percent_done=100)
    qs5 = qs.filter(Q(is_forked=True)|Q(is_original=True)).filter(subtitleversion__isnull=False)
    
    mqs = TeamMultyQuerySet(qs1, qs2, qs3, qs4, qs5, qs_complement)
    
    extra_context = widget.add_onsite_js_files({})    
    extra_context.update({
        'team': team,
        'can_edit_video': team.can_edit_video(request.user)
    })
    
    if qs1.count() + qs2.count() + qs3.count() + qs4.count() + qs5.count() == 0:
        mqs = SubtitleLanguage.objects.filter(video__in=video_ids).filter(is_original=True)
        extra_context['allow_noone_language'] = True

    if team.video:
        extra_context['widget_params'] = base_widget_params(request, {
            'video_url': team.video.get_video_url(), 
            'base_state': {}
        })
        
    return object_list(request, queryset=mqs, 
                       paginate_by=VIDEOS_ON_PAGE, 
                       template_name='teams/detail.html', 
                       extra_context=extra_context, 
                       template_object_name='team_video_lang')

def detail_members(request, slug):
    #just other tab of detail view
    q = request.REQUEST.get('q')
    
    team = Team.get(slug, request.user)
    
    qs = team.members.all()
    if q:
        qs = qs.filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q) \
                       |Q(user__username__icontains=q)|Q(user__biography__icontains=q))

    extra_context = widget.add_onsite_js_files({})  

    extra_context.update({
        'team': team,
        'query': q
    })
    
    if team.video:
        extra_context['widget_params'] = base_widget_params(request, {
            'video_url': team.video.get_video_url(), 
            'base_state': {}
        })    
    return object_list(request, queryset=qs, 
                       paginate_by=MEMBERS_ON_PAGE, 
                       template_name='teams/detail_members.html', 
                       extra_context=extra_context, 
                       template_object_name='team_member')

def videos_actions(request, slug):
    team = Team.get(slug, request.user)  
    videos_ids = team.teamvideo_set.values_list('video__id', flat=True)
    qs = Action.objects.filter(video__pk__in=videos_ids)
    extra_context = {
        'team': team
    }   
    return object_list(request, queryset=qs, 
                       paginate_by=ACTIONS_ON_PAGE, 
                       template_name='teams/videos_actions.html', 
                       extra_context=extra_context, 
                       template_object_name='videos_action')

def members_actions(request, slug):
    team = Team.get(slug, request.user)   
    
    user_ids = team.members.values_list('user__id', flat=True)
    
    qs = Action.objects.filter(user__pk__in=user_ids)
    
    extra_context = {
        'team': team
    }   
    return object_list(request, queryset=qs, 
                       paginate_by=ACTIONS_ON_PAGE, 
                       template_name='teams/members_actions.html', 
                       extra_context=extra_context, 
                       template_object_name='action')

@render_to('teams/create.html')
@login_required    
def create(request):
    user = request.user
    
    if not DEV and not (user.is_superuser and user.is_active):
        raise Http404 
    
    if request.method == 'POST':
        form = CreateTeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(user)
            messages.success(request, _('Your team has been created. Review or edit its information below.'))
            return redirect(team.get_edit_url())
    else:
        form = CreateTeamForm()
    return {
        'form': form
    }

@render_to('teams/edit.html')
@login_required
def edit(request, slug):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404
    
    if not team.is_manager(request.user):
        return {
            'team': team
        }
    
    if request.method == 'POST':
        if request.user.is_staff:
            form = EditTeamFormAdmin(request.POST, request.FILES, instance=team)
        else:
            form = EditTeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, _('Team edited success'))
            return redirect(team.get_edit_url())
    else:
        if request.user.is_staff:
            form = EditTeamFormAdmin(instance=team)
        else:
            form = EditTeamForm(instance=team)
    return {
        'form': form,
        'team': team
    }

@login_required
def edit_logo(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        raise Http404
    
    output = {}
    form = EditLogoForm(request.POST, instance=team, files=request.FILES)
    if form.is_valid():
        try:
            form.save()
            output['url'] =  str(team.logo_thumbnail())
        except S3StorageError:
            output['error'] = {'logo': ugettext(u'File server unavailable. Try later. You can edit some other information without any problem.')}
    else:
        output['error'] = form.get_errors()
    return HttpResponse('<textarea>%s</textarea>'  % json.dumps(output))

@render_to('teams/add_video.html')
@login_required
def add_video(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        raise Http404
    
    if not team.can_add_video(request.user):
        messages.error(request, _(u'You can\'t add video.'))
        return {
            'team': team
        }
    
    initial = {
        'video_url': request.GET.get('url', ''),
        'title': request.GET.get('title', '')
    }
    
    form = AddTeamVideoForm(team, request.POST or None, request.FILES or None, initial=initial)
    
    if form.is_valid():
        obj =  form.save(False)
        obj.added_by = request.user
        obj.save()  
        return redirect(obj)
        
    return {
        'form': form,
        'team': team
    }

@login_required
def edit_videos(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        raise Http404
    
    qs = team.teamvideo_set.all()
    
    extra_context = {
        'team': team,
    }
    return object_list(request, queryset=qs,
                       paginate_by=VIDEOS_ON_PAGE,
                       template_name='teams/edit_videos.html',
                       template_object_name='videos',
                       extra_context=extra_context)

@login_required
@render_to('teams/team_video.html')
def team_video(request, team_video_pk):
    team_video = get_object_or_404(TeamVideo, pk=team_video_pk)
    
    if not team_video.can_edit(request.user):
        raise Http404
    
    form = EditTeamVideoForm(request.POST or None, request.FILES or None, instance=team_video)

    if form.is_valid():
        form.save()
        messages.success(request, _('Video has been updated.'))
        return redirect(team_video)

    context = widget.add_onsite_js_files({})
    
    context.update({
        'team': team_video.team,
        'team_video': team_video,
        'form': form,
        'widget_params': base_widget_params(request, {'video_url': team_video.video.get_video_url(), 'base_state': {}})
    })
    return context

@render_to_json
@login_required    
def remove_video(request, team_video_pk):
    team_video = get_object_or_404(TeamVideo, pk=team_video_pk)

    if not team_video.team.is_member(request.user):
        raise Http404
    
    if team_video.can_remove(request.user):
        team_video.delete()
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
def remove_member(request, slug, user_pk):
    team = Team.get(slug, request.user)

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
def demote_member(request, slug, user_pk):
    team = Team.get(slug, request.user)

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
    return redirect('teams:edit_members', team.slug)

@login_required
def promote_member(request, slug, user_pk):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404

    if team.is_manager(request.user):
        user = get_object_or_404(User, pk=user_pk)
        if not user == request.user:
            TeamMember.objects.filter(team=team, user=user).update(is_manager=True)
    else:
        messages.error(request, _('You can\'t promote to manager'))
    return redirect('teams:edit_members', team.slug)

@login_required        
def edit_members(request, slug):
    team = Team.get(slug, request.user)
    
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
                       paginate_by=MEMBERS_ON_PAGE,
                       template_name='teams/edit_members.html',
                       template_object_name='members',
                       extra_context=extra_context)    

@login_required
def applications(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        raise Http404
    
    qs = team.applications.all()
        
    extra_context = {
        'team': team
    }
    return object_list(request, queryset=qs,
                       paginate_by=APLICATIONS_ON_PAGE,
                       template_name='teams/applications.html',
                       template_object_name='applications',
                       extra_context=extra_context) 

@login_required
def approve_application(request, slug, user_pk):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404
    
    if team.can_approve_application(request.user):
        try:
            Application.objects.get(team=team, user=user_pk).approve()
            messages.success(request, _(u'Application approved.'))
        except Application.DoesNotExist:
            messages.error(request, _(u'Application does not exist.'))
    else:
        messages.error(request, _(u'You can\'t approve application.'))
    return redirect('teams:applications', team.pk)

@login_required
def deny_application(request, slug, user_pk):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404
    
    if team.can_approve_application(request.user):
        try:
            Application.objects.get(team=team, user=user_pk).deny()
            messages.success(request, _(u'Application denied.'))
        except Application.DoesNotExist:
            messages.error(request, _(u'Application does not exist.'))
    else:
        messages.error(request, _(u'You can\'t deny application.'))
    return redirect('teams:applications', team.pk)

@render_to_json
@login_required
def invite(request):
    team_pk = request.POST.get('team_id')
    username = request.POST.get('username')
    note = request.POST.get('note', '')
    
    if not team_pk and not username:
        raise Http404
    
    team = get_object_or_404(Team, pk=team_pk)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return {
            'error': ugettext(u'User does not exist.')
        }
    
    if not team.can_invite(request.user):
        return {
            'error': ugettext(u'You can\'t invite to team.')
        }
        
    if team.is_member(user):
        return {
            'error': ugettext(u'This user is member of team already.')
        }
    
    if len(note) > Invite._meta.get_field('note').max_length:
        return {
            'error': ugettext(u'Note is too long.')
        }        
        
    Invite.objects.get_or_create(team=team, user=user, defaults={'note': note})
    return {}

@login_required
def accept_invite(request, invite_pk, accept=True):
    invite = get_object_or_404(Invite, pk=invite_pk, user=request.user)
    
    if accept:
        invite.accept()
    else:
        invite.deny()
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

@permission_required('teams.change_team')
def highlight(request, slug, highlight=True):
    item = get_object_or_404(Team, slug=slug)
    item.highlight = highlight
    item.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def join_team(request, slug):
    team = get_object_or_404(Team, slug=slug)
    response = TeamsApi.join(team.pk, request.user)
    
    if response.get('error'):
        messages.error(request, response.get('error'))
        
    if response.get('msg'):
        messages.success(request, response.get('msg'))
    
    return redirect(team)