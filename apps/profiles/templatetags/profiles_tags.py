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
from videos.models import Action
from django.conf import settings
from auth.models import CustomUser as User
from profiles.forms import SelectLanguageForm
from utils.translation import get_user_languages_from_request, get_user_languages_from_cookie
from rosetta.views import can_translate as can_translate_func

register = template.Library()

ACTIONS_ON_PAGE = getattr(settings, 'ACTIONS_ON_PAGE', 10)

@register.filter
def can_translate(user):
    return can_translate_func(user)

@register.inclusion_tag('profiles/_require_email_dialog.html', takes_context=True)
def require_email_dialog(context):
    return context

@register.inclusion_tag('profiles/_select_language_dialog.html', takes_context=True)
def select_language_dialog(context, option=None):
    user_langs = get_user_languages_from_request(context['request'])

    initial_data = {}
    
    for i, l in enumerate(user_langs):
        initial_data['language%s' % (i+1)] = l
        
    form = SelectLanguageForm(initial=initial_data)

    return {
        'form': form,
        'force_ask': (option == 'force') and _user_needs_languages(context)
    }

def _user_needs_languages(context):
    user = context['user']
    if user.is_authenticated():
        return not user.userlanguage_set.exists()
    else:
        return not bool(get_user_languages_from_cookie(context['request']))

@register.inclusion_tag('profiles/_user_videos_activity.html', takes_context=True)
def user_videos_activity(context, user=None):
    user = user or context['user']
    
    if user.is_authenticated():
        context['users_actions'] = Action.objects.select_related('video', 'language', 'language__video', 'user') \
            .filter(video__customuser=user) \
            .exclude(user=user) \
            .exclude(user=User.get_anonymous())[:ACTIONS_ON_PAGE]
    else:
        context['users_actions'] = Action.objects.none()
    return context

@register.inclusion_tag('profiles/_send_message.html', takes_context=True)
def send_message(context):
    return {
        'user': context['user']
    }

@register.inclusion_tag('profiles/_user_avatar.html', takes_context=True)    
def user_avatar(context, user_obj):
    return {
        'user': context['user'],
        'user_obj':user_obj
    }

@register.inclusion_tag('profiles/_top_user_panel.html', takes_context=True)
def top_user_panel(context):
    return context
