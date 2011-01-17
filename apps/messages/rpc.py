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

from messages.models import Message
from auth.models import CustomUser as User
from django.utils.translation import ugettext as _
from messages.forms import SendMessageForm

class MessagesApiClass(object):
    
    def remove(self, message_id, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}
        
        try:
            msg = Message.objects.for_user(user).get(pk=message_id)
            msg.delete_for_user(user)
        except Message.DoesNotExist:
            return {'error': _('Message does not exist.')}
        
        return {}
    
    def mark_as_read(self, message_id, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}
        
        Message.objects.filter(pk=message_id, user=user).update(read=True)
        
        return {}
    
    def send(self, rdata, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}
        
        form = SendMessageForm(user, rdata)
        if form.is_valid():
            form.save()
            return {}
        else:
            return {
                'errors': form.get_errors()
            }
        
        return {}
        