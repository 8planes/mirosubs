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
from messages.models import Message
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic.list_detail import object_list
from messages.rpc import MessagesApiClass
from utils.rpc import RpcRouter
from messages.forms import SendMessageForm


rpc_router = RpcRouter('messages:rpc_router', {
    'MessagesApi': MessagesApiClass()
})

MESSAGES_ON_PAGE = getattr(settings, 'MESSAGES_ON_PAGE', 30)


@login_required
def index(request, message_pk=None):
    user = request.user
    qs = Message.objects.for_user(user)

    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True
    }
    
    reply = request.GET.get('reply')

    if reply:
        try:
            reply_msg = Message.objects.get(pk=reply, user=user)
            reply_msg.read = True
            reply_msg.save()
            extra_context['reply_msg'] = reply_msg
        except (Message.DoesNotExist, ValueError):
            pass

    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/index.html',
                       template_object_name='message',
                       extra_context=extra_context)
    
@login_required    
def sent(request):
    qs = Message.objects.for_author(request.user)
    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True        
    }
    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/sent.html',
                       template_object_name='message',
                       extra_context=extra_context)    
