from django import template
from videos.forms import FeedbackForm

register = template.Library()

@register.inclusion_tag('videos/_feedback_form.html')
def feedback_form():
    return {
        'form': FeedbackForm()
    }