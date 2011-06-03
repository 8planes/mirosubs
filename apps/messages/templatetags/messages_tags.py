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
from messages.models import Message
from messages.forms import SendMessageForm, SendTeamMessageForm

register = template.Library()

@register.inclusion_tag('messages/_messages.html', takes_context=True)    
def messages(context):
    user = context['user']
    if user.is_authenticated():
        qs = user.unread_messages()
    else:
        qs = Message.objects.none()
    return {
        'msg_count': qs.count()
    }

@register.inclusion_tag('messages/_send_message_form.html', takes_context=True)    
def send_message_form(context, receiver):
    context['send_message_form'] = SendMessageForm(context['user'], initial={'user': receiver.pk})
    context['receiver'] = receiver
    context['form_id'] = 'send-message-form-%s' % receiver.pk
    return context

@register.inclusion_tag('messages/_send_to_team_message_form.html', takes_context=True)    
def send_to_team_message_form(context, team):
    context['send_message_form'] = SendTeamMessageForm(context['user'], initial={'team': team})
    context['form_id'] = 'send-message-to-team-form-%s' % team.pk
    context['team'] = team
    return context    