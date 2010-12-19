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
from videos.models import Video
from auth.models import CustomUser as User

register = template.Library()

ACTIONS_ON_PAGE = getattr(settings, 'ACTIONS_ON_PAGE', 10)

@register.inclusion_tag('profiles/_user_videos_activity.html', takes_context=True)
def user_videos_activity(context, user=None):
    user = user or context['user']
    
    if user.is_authenticated():
        videos_ids = Video.objects.filter(subtitlelanguage__subtitleversion__user=user).distinct() \
            .values_list('id', flat=True)
        context['users_actions'] = Action.objects.filter(video__pk__in=videos_ids) \
            .exclude(user=user) \
            .exclude(user=User.get_youtube_anonymous())[:ACTIONS_ON_PAGE]
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