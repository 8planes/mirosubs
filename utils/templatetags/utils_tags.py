from django import template
from django.db import connection
from django.utils.translation import ugettext

register = template.Library()

@register.simple_tag
def form_field_as_list(GET_vars, bounded_field, count=0):
    getvars = '?'
    
    if len(GET_vars.keys()) > 0:
        getvars = "?%s&" % GET_vars.urlencode()
    
    output = []
    
    data = bounded_field.data or bounded_field.field.initial

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
            'fname': bounded_field.html_name,
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



def parse_tokens(parser, bits):
    """
    Parse a tag bits (split tokens) and return a list on kwargs (from bits of the  fu=bar) and a list of arguments.
    """

    kwargs = {}
    args = []
    for bit in bits[1:]:
        try:
            try:
                pair = bit.split('=')
                kwargs[str(pair[0])] = parser.compile_filter(pair[1])
            except IndexError:
                args.append(parser.compile_filter(bit))
        except TypeError:
            raise template.TemplateSyntaxError('Bad argument "%s" for tag "%s"' % (bit, bits[0]))

    return args, kwargs

class ZipLongestNode(template.Node):
    """
    Zip multiple lists into one using the longest to determine the size

    Usage: {% zip_longest list1 list2 <list3...> as items %}
    """
    def __init__(self, *args, **kwargs):
        self.lists = args
        self.varname = kwargs['varname']

    def render(self, context):
        lists = [e.resolve(context) for e in self.lists]

        if self.varname is not None:
            context[self.varname] = [i for i in map(lambda *a: a, *lists)]
        return ''

@register.tag
def zip_longest(parser, token):
    bits = token.contents.split()
    varname = None
    if bits[-2] == 'as':
        varname = bits[-1]
        del bits[-2:]
    else:
        # raise exception
        pass
    args, kwargs = parse_tokens(parser, bits)

    if varname:
        kwargs['varname'] = varname

    return ZipLongestNode(*args, **kwargs)

# from http://djangosnippets.org/snippets/1518/
# watchout, if you change the site domain this value will get stale
domain = "http://%s" % Site.objects.get_current().domain

class AbsoluteURLNode(URLNode):
    def render(self, context):
        if self.asvar:  
            context[self.asvar]= urlparse.urljoin(domain, context[self.asvar])  
            return ''  
        else:  
            return urlparse.urljoin(domain, path)
        path = super(AbsoluteURLNode, self).render(context)
        domain = "http://%s" % Site.objects.get_current().domain
        return urlparse.urljoin(domain, path)

def absurl(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)
absurl = register.tag(absurl)        


