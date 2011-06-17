from django import template
from videos.forms import FeedbackForm

register = template.Library()

@register.inclusion_tag('videos/_feedback_form.html')
def feedback_form():
    return {
        'form': FeedbackForm(auto_id="feedback_%s", label_suffix="")
    }
    
@register.inclusion_tag('videos/_error_feedback_form.html')
def error_feedback_form(error):
    form = FeedbackForm(auto_id="feedback_%s", label_suffix="", initial={
        'error': error
    }, hide_captcha=True)
    return {
        'form': form,
        'error': error
    }
