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

register = template.Library()

class EscapeJSNode(template.Node):
    def __init__(self, nodelist):
           self.nodelist = nodelist
    
    def render(self, context):
        from django.template.defaultfilters import escapejs
        return escapejs(self.nodelist.render(context).strip())
        
@register.tag
def escapejs(parser, token):
    """
    Escapes characters for use in JavaScript strings.
    
    Sample usage::
    {% escapejs %}
        <p>
            Text to<br />
            <a href="#">escape</a> here.
        </p>
    {% endescapejs %}
    """
    nodelist = parser.parse(('endescapejs',))
    parser.delete_first_token()
    return EscapeJSNode(nodelist)


