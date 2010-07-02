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
from django.template import RequestContext
from apps.widget.views import base_widget_params

register = template.Library()

@register.inclusion_tag('videos/_widget.html', takes_context=True)
def widget(context, video_url, div_id='widget_div'):
    extra_params = {}
    if context['request'].GET.get('autosub') == 'true':
        extra_params['subtitle_immediately'] = True
    widget_params = base_widget_params(context['request'], video_url, extra_params)
    return {
        'div_id': div_id,
        'widget_params': widget_params
    }