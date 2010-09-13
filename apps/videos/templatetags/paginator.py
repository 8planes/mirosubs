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

register = template.Library()

def paginator(context, adjacent_pages=3):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    startPage = max(context['page'] - adjacent_pages, 1)
    if startPage <= 3: startPage = 1
    endPage = context['page'] + adjacent_pages + 1
    if endPage >= context['pages'] - 1: endPage = context['pages'] + 1
    page_numbers = [n for n in range(startPage, endPage) \
            if n > 0 and n <= context['pages']]
    page_obj = context['page_obj']
    paginator = context['paginator']

    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
    }

register.inclusion_tag('_paginator.html', takes_context=True)(paginator)

def search_ordered_paginator(context, query, adjacent_pages=2):
    return ordered_paginator(context, adjacent_pages, q=query)
register.inclusion_tag('_ordered_paginator.html', takes_context=True)(search_ordered_paginator)

def ordered_paginator(context, adjacent_pages=3, anchor='', **kwargs):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    startPage = max(context['page'] - adjacent_pages, 1)
    if startPage <= 3: startPage = 1
    endPage = context['page'] + adjacent_pages + 1
    if endPage >= context['pages'] - 1: endPage = context['pages'] + 1
    page_numbers = [n for n in range(startPage, endPage) \
            if n > 0 and n <= context['pages']]
    page_obj = context['page_obj']
    paginator = context['paginator']
    
    ordering = context.has_key('ordering') and context['ordering']
    order_type = context.has_key('order_type') and context['order_type']
    
    extra_link = ''
    if ordering:
         extra_link = '&o=%s' % ordering
         if order_type:
             extra_link += '&ot=%s' % order_type
    
    for key, value in kwargs.items():
        extra_link += '&%s=%s' % (key, value)
    
    extra_link += anchor
                
    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
        'extra_link': extra_link
    }

register.inclusion_tag('_ordered_paginator.html', takes_context=True)(ordered_paginator)

@register.tag
def ordered_column(parser, token):
    try:
        tokens = token.split_contents()
        field_name = tokens[1]
        title = tokens[2]
        get_params = tokens[3:]
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return OrderedColumnNode(parser.compile_filter(field_name), parser.compile_filter(title), get_params)
    
class OrderedColumnNode(template.Node):
    
    def __init__(self, field_name, title, get_params):
        self.field_name = field_name
        self.title = title
        self.page = template.Variable('page')
        self.order_type = template.Variable('order_type')
        self.ordering = template.Variable('ordering')
        self.get_params = get_params
        
    def render(self, context):
        if context.has_key(self.page.var):
            page = self.page.resolve(context)
        else:
            page = None
        
        if context.has_key(self.ordering.var):
            ordering = self.ordering.resolve(context)
        else:
            ordering = None
                    
        if context.has_key(self.order_type.var):
            order_type = self.order_type.resolve(context)
        else:
            order_type = None
        
        extra_params = [] 
        anchor = ''
        for item in self.get_params:
            if item.startswith('#'):
                anchor = item
            else:
                items = item.split('=')
                variable = template.Variable(items[1])
                extra_params.append('&%s=%s' % (items[0], variable.resolve(context)))
        
        extra_params = ''.join(extra_params)+anchor
        field_name = self.field_name.resolve(context, True)
        
        ot = (ordering == field_name and order_type == 'desc') and 'asc' or 'desc'
        if page:
            link = '?o=%s&ot=%s&page=%s%s' % (field_name, ot, page, extra_params)
        else:
            link = '?o=%s&ot=%s%s' % (field_name, ot, extra_params)
        return '<a href="%s" class="%s">%s</a>' % (link, ot, self.title.resolve(context, True))

@register.simple_tag   
def progress_color(value):
    if value <= 50:
        return 'red'
    if value >= 90:
        return 'green'
    return 'yellow'