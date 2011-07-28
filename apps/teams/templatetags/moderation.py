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

import json

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django import template
from django.template.loader import render_to_string

register = template.Library()

from apps.teams.moderation import  APPROVED, WAITING_MODERATION
from apps.teams.moderation import   user_can_moderate as _user_can_moderate

from apps.videos.models import SubtitleLanguage, SubtitleVersion



@register.inclusion_tag("moderation/_remove_approval_button.html")
def render_remove_approve_button(version_or_language):
    if isinstance(version_or_language, SubtitleVersion):
        version = version_or_language
    elif isinstance(version_or_language, SubtitleLanguage):
        version = version_or_language.latest(public_only=False)

    team = version.video.moderated_by
    return {
        "team": team,
        "version": version
        }

@register.inclusion_tag("moderation/_approve_button.html")
def render_approve_button(version_or_list):
    if isinstance(version_or_list, SubtitleVersion):
        team = version_or_list.language.video.moderated_by
        url = reverse("moderation:revision-approve", kwargs={'team_id':team.pk, "version_id":version_or_list.pk})
        label = _("Approve")
    elif isinstance(version_or_list, list):
        # we will approve all revisions unitl this one, as this is what the moderator saw on the review subs panel
        team = version_or_list[0].language.video.moderated_by_id
        label = _("Approve  revisions")
        url = reverse("moderation:revision-approve-batch-until", kwargs={
                'team_id':team,
                "before_rev": version_or_list[0].pk,
                "lang_id":version_or_list[0].language.pk,
        })
    return {
        "label": label,
        "team": team,
        "url": url
        }

@register.inclusion_tag("moderation/_approve_button.html")
def render_approve_button_lang(team, lang_pk, latest_version_pk):

    label = _("Approve  revisions")
    url = reverse("moderation:revision-approve-batch-until", kwargs={
            'team_id':team,
            "before_rev": latest_version_pk,
            "lang_id":lang_pk
        })
    return {
        "label": label,
        "team": team,
        "url": url
        }

@register.inclusion_tag("moderation/_reject_button.html")
def render_reject_button_lang(team, lang_pk, latest_version_pk):
    label = _("Approve  revisions")
    url = reverse("moderation:revision-reject-batch-until", kwargs={
            'team_id':team,
            "before_rev": latest_version_pk,
            "lang_id":lang_pk
        })
    return {
        "style":"labelless",
        "label": label,
        "team": team,
        "url": url
        }

@register.inclusion_tag("moderation/_reject_button.html")
def render_reject_button(version_or_language, label=None, confirms=False):
    if isinstance(version_or_language, SubtitleVersion):
        version = version_or_language
    elif isinstance(version_or_language, SubtitleLanguage):
        version = version_or_language.latest(public_only=False)


    team = version.video.moderated_by
    url = reverse("moderation:revision-reject", kwargs={
            'team_id':team.pk,
            "version_id": version.pk,
        })
    return {
        "team": team,
        "version": version,
        "label": label or "Decline revision",
        "confirms": confirms,
        "url": url,
       } 
    

@register.inclusion_tag("moderation/_approval_toolbar.html")
def render_approval_toolbar( user, version):
    if version is None:
        return {}
    team = version.video.moderated_by        
    can_moderate = _user_can_moderate(version.language.video,  user)
    if not team or not  can_moderate:
        return {
            
        }
    return {
        "version":version,
        "team": team,
        "is_approved": version.moderation_status == APPROVED
    }
    
    
    
@register.simple_tag
def versions_to_moderate(team):
    return team.get_pending_moderation().order_by("language__video", "language").select_related("language", "language__video")

@register.simple_tag
def versions_to_moderate_count(team):
    return team.get_pending_moderation().count()

@register.simple_tag#inclusion_tag("moderation/_moderation_status_icon.html")
def render_moderation_icon(version):
    return render_to_string("moderation/_moderation_status_icon.html",  {
        "is_moderated" :  version.language.video.is_moderated,
        "status": version.moderation_status
    })

@register.simple_tag
def render_moderation_togggle_button(version):
    approved = version.moderation_status == APPROVED
    label = ""
    
    if approved:
        template_name = "moderation/_reject_button.html"
        label = _("Reject")
        url = reverse("moderation:revision-reject", kwargs={'team_id':version.video.moderated_by_id, "version_id":version.pk})
    else:
        template_name = "moderation/_approve_button.html"
        label = _("Approve")
        url = reverse("moderation:revision-approve", kwargs={'team_id':version.video.moderated_by_id, "version_id":version.pk})
        
    return render_to_string(template_name, {
            "label": label,
            "url" : url,
    })

@register.simple_tag
def user_can_moderate( user, video, team):
    return _user_can_moderate(video,  user)


                    
def parse_tokens(parser, bits):
    """
    Parse a tag bits (split tokens) and return a list on kwargs (from bits of the  fu=bar) and a list of arguments.
    """

    kwargs = {}
    args = []
    for bit in bits[1:]:
        try:
            try:
                pair = bit.split('=')
                kwargs[str(pair[0])] = parser.compile_filter(pair[1])
            except IndexError:
                args.append(parser.compile_filter(bit))
        except TypeError:
            raise template.TemplateSyntaxError('Bad argument "%s" for tag "%s"' % (bit, bits[0]))

    return args, kwargs

class ModerationInfoNode(template.Node):
    """
    Zip multiple lists into one using the longest to determine the size

    Usage: {% zip_longest list1 list2 <list3...> as items %}
    """
    def __init__(self, team_video_index, **kwargs):
        self.team_video_index = team_video_index
        self.varname = kwargs['varname']

    def render(self, context):
        team_video_index = self.team_video_index.resolve(context) 

        if self.varname is not None:
            context[self.varname] = _dehidrate_versions(team_video_index)
        return ''

@register.simple_tag
def is_moderated(version_lang_or_video):
    is_moderated(version_lang_or_video)

def _dehidrate_versions(search_index):
    x = []
    if bool(search_index.moderation_version_info) is False:
        return
    versions =   json.loads(search_index.moderation_version_info)
    i = 0
    for lang_name, lang_pk, versions in zip(search_index.moderation_languages_names,\
            search_index.moderation_languages_pks, versions):
        x.append({
            "name": lang_name,
            "pk":lang_pk,
            "versions": versions,
            "latest_version_pk": versions[0]['pk']
            })

    return x

@register.tag
def dehidrate_versions(parser, token):
    bits = token.contents.split()
    varname = None
    if bits[-2] == 'as':
        varname = bits[-1]
        del bits[-2:]
    else:
        # raise exception
        pass
    args, kwargs = parse_tokens(parser, bits)

    if varname:
        kwargs['varname'] = varname

    return ModerationInfoNode(args[0], **kwargs)

@register.inclusion_tag("moderation/_videos_to_moderate.html")
def render_moderation_search_results(result_list):
    return {
        "result_list": result_list
    }

