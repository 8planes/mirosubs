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
    message = None
    if message_pk is not None:
        try:
            message = Message.objects.for_user(request.user).get(pk=message_pk)
        except Message.DoesNotExist:
            pass
    qs = Message.objects.for_user(request.user).filter(user=request.user)
    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True,
        "show_message" : message
    }
    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/index.html',
                       template_object_name='message',
                       extra_context=extra_context)
def message_detail(request, message_pk):
    return index(request, message_pk)

@login_required    
def sent(request):
    qs = Message.objects.for_user(request.user).filter(author=request.user)
    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True        
    }
    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/sent.html',
                       template_object_name='message',
                       extra_context=extra_context)    
