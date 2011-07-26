from django import template
from django.db import connection
from django.utils.translation import ugettext

register = template.Library()

@register.simple_tag
def form_field_as_list(GET_vars, bounded_field, count=0):
    getvars = '?'
    
    if bounded_field.name in GET_vars:
        del GET_vars[bounded_field.name]
    
    if len(GET_vars.keys()) > 0:
        getvars = "?%s&" % GET_vars.urlencode()
    
    output = []
    data = bounded_field.data or bounded_field.field.initial and bounded_field.field.initial

    for i, choice in enumerate(bounded_field.field.choices):
        if choice[0] == data:
            li_attrs = u'class="active"'
        else:
            li_attrs = u''
        
        href = u'%s%s=%s' % (getvars, bounded_field.name, choice[0])
        li = {
            'attrs': li_attrs,
            'href': href,
            'value': choice[0],
            'fname': bounded_field.name,
            'name': choice[1]
        }
        
        if count and choice[0] == data and i >= count:
            output.insert(count - 1, li)
        else:
            output.append(li)

    if count:
        li = {
            'attrs': u'class="more-link"',
            'href': '#',
            'name': ugettext(u'more...'),
            'fname': '',
            'value': ''
        }        
        output.insert(count, li)
        
        for i in xrange(len(output[count+1:])):
            output[count+i+1]['attrs'] += u' style="display: none"'

    content = [u'<ul>']
    for item in output:
        content.append(u'<li %(attrs)s><a href="%(href)s" name="%(fname)s" value="%(value)s"><span>%(name)s</span></a></li>' % item) 
    content.append(u'</ul>')
    
    return u''.join(content)