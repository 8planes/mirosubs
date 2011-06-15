from django.utils.encoding import force_unicode    
from django import forms
from django.core import validators
from utils.validators import UniSubURLValidator
from django.utils.translation import ugettext_lazy as _
from utils.forms.recapcha import ReCaptchaField
import re

class AjaxForm(object):
    
    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output

class StripRegexField(forms.RegexField):

    def to_python(self, value):
        value = super(StripRegexField, self).to_python(value)
        return value.strip()

class StripURLField(forms.URLField):
    
    def to_python(self, value):
        value = super(StripURLField, self).to_python(value)
        return value.strip()

class FeedURLValidator(validators.URLValidator):
    regex = re.compile(
        r'^(?:(?:https?)|(?:feed))://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)    

class FeedURLField(forms.URLField):

    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=validators.URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        forms.CharField.__init__(self,max_length, min_length, *args,
                                       **kwargs)
        self.validators.append(FeedURLValidator(verify_exists=verify_exists, validator_user_agent=validator_user_agent))

    def to_python(self, value):
        value = super(FeedURLField, self).to_python(value)
        return value.strip()
    
class UniSubURLField(StripURLField):
    
    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=validators.URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        super(forms.URLField, self).__init__(max_length, min_length, *args,
                                       **kwargs)
        self.validators.append(UniSubURLValidator(verify_exists=verify_exists, validator_user_agent=validator_user_agent))

class ListField(forms.RegexField):

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super(ListField, self).__init__(self.pattern, max_length, min_length, *args, **kwargs)

    def clean(self, value):
        if value:
            value = value and value.endswith(',') and value or value+','
            value = value.replace(' ', '')
        value = super(ListField, self).clean(value)
        return [item for item in value.strip(',').split(',') if item]
        
email_list_re = re.compile(
    r"""^(([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6},)+$""", re.IGNORECASE)

class EmailListField(ListField):
    default_error_messages = {
        'invalid': _(u'Enter valid e-mail addresses separated by commas.')
    }
    pattern = email_list_re
    
username_list_re = re.compile(r'^([A-Z0-9]+,)+$', re.IGNORECASE)

class UsernameListField(ListField):
    default_error_messages = {
        'invalid': _(u'Enter valid usernames separated by commas. Username can contain only a-z, A-Z and 0-9.')
    }
    pattern = username_list_re
    
        