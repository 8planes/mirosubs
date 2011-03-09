from django import template
from django.db import connection

register = template.Library()

@register.simple_tag
def print_query_count(key):
    print '>>>> %s: %s' % (key, len(connection.queries))
    return ''