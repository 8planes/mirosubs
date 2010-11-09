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
from utils import render_to
from messages.models import Message
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic.list_detail import object_list

MESSAGES_ON_PAGE = getattr(settings, 'MESSAGES_ON_PAGE', 30)

@login_required
def index(request):
    qs = Message.objects.filter(user=request.user)
    qs.update(read=True)
    extra_context = {}
    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/index.html',
                       template_object_name='message',
                       extra_context=extra_context)