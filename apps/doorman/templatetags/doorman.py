from django import template
import datetime

register = template.Library()

from apps.doorman import feature_is_on

class FeatureSwitchNode(template.Node):
    def __init__(self, flag_name, nodelist, request):
        self.flag_name = flag_name.upper()
        self.request = request
        self.nodelist = nodelist

    def render(self, context):
        if feature_is_on(self.flag_name, self.request):
            output = self.nodelist.render(context)
            return output
        return ""

@register.tag
def switch_feature(parser, token):
    nodelist = parser.parse(('endswitch_feature',))
    parser.delete_first_token()
    parts = token.split_contents()
    flag_name = parts[1]
    if len(parts) > 2:
        request = parts [2]
    else:
        request = None

    return FeatureSwitchNode(flag_name, nodelist, request)

class CommentNode(template.Node):
    def render(self, context):
        return ''    
