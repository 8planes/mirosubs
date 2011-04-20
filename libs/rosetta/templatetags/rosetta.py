from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re
from django.template import Node
from django.utils.encoding import smart_str, smart_unicode

register = template.Library()
rx = re.compile(r'(%(\([^\s\)]*\))?[sd])')

def format_message(message):
    return mark_safe(rx.sub('<code>\\1</code>', escape(message).replace(r'\n','<br />\n')))
format_message=register.filter(format_message)


def lines_count(message):
    return 1 + sum([len(line)/50 for line in message.split('\n')])
lines_count=register.filter(lines_count)

def mult(a,b):
    return int(a)*int(b)
mult=register.filter(mult)

def minus(a,b):
    try:
        return int(a) - int(b)
    except:
        return 0
minus=register.filter(minus)
    

def gt(a,b):
    try:
        return int(a) > int(b)
    except:
        return False
gt=register.filter(gt)


def do_incr(parser, token):
    args = token.split_contents()
    if len(args) < 2:
        raise TemplateSyntaxError("'incr' tag requires at least one argument")
    name = args[1]
    if not hasattr(parser, '_namedIncrNodes'):
        parser._namedIncrNodes = {}
    if not name in parser._namedIncrNodes:
        parser._namedIncrNodes[name] = IncrNode(0)
    return parser._namedIncrNodes[name]
do_incr = register.tag('increment', do_incr)


class IncrNode(template.Node):
   def __init__(self, init_val=0):
       self.val = init_val

   def render(self, context):
       self.val += 1
       return smart_unicode(self.val)
       
    
def is_fuzzy(message):
    return message and hasattr(message, 'flags') and 'fuzzy' in message.flags
is_fuzzy = register.filter(is_fuzzy)

class RosettaCsrfTokenPlaceholder(Node):
    def render(self, context):
        return mark_safe(u"<!-- csrf token placeholder -->")

def rosetta_csrf_token(parser, token):
    try:
        from django.template.defaulttags import csrf_token
        return csrf_token(parser,token)
    except ImportError:
        return RosettaCsrfTokenPlaceholder()
rosetta_csrf_token=register.tag(rosetta_csrf_token)
