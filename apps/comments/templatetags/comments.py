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

from django import template
from apps.comments.forms import CommentForm
from apps.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.inclusion_tag('comments/form.html', takes_context=True)
def render_comment_form(context, obj):
    form = CommentForm(obj, auto_id='id_comment_form_%s')
    return {
        'form': form,
        'is_authnticated': context['user'].is_authenticated(),
        'next_page': context['request'].get_full_path()
    }

@register.inclusion_tag('comments/list.html', takes_context=True)
def render_comment_list(context, obj):
    return {
        'qs': Comment.get_for_object(obj),
        'content_type': ContentType.objects.get_for_model(obj),
        'obj': obj
    }
    
@register.simple_tag    
def get_comment_count(obj):
    return Comment.get_for_object(obj).count()