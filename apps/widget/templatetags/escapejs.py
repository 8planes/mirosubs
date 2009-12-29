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


