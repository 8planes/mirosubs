from django import template
from django.db import connection

register = template.Library()

@register.simple_tag
def form_field_as_list(request, bounded_field):
    getvars = '?'
    
    GET_vars = request.GET.copy()
    if bounded_field.name in GET_vars:
        del GET_vars[bounded_field.name]
    
    if len(GET_vars.keys()) > 0:
        getvars = "?%s" % GET_vars.urlencode()
    
    output = [u'<ul>']
    data = bounded_field.data or bounded_field.field.initial and bounded_field.field.initial

    for choice in bounded_field.field.choices:
        if choice[0] == data:
            li_attrs = u'class="active"'
        else:
            li_attrs = u''
        
        href = u'%s&%s=%s' % (getvars, bounded_field.name, choice[0])
        li = u'<li %s><a href="%s">%s</a></li>' % (li_attrs, href, choice[1])
        output.append(li)
        
    output.append(u'</ul>')
    
    return u''.join(output)