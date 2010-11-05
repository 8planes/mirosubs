from django.utils.encoding import force_unicode    
from django import forms
from django.core import validators
from utils.validators import UniSubURLValidator

class AjaxForm(object):
    
    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class UniSubURLField(forms.URLField):
    
    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=validators.URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        super(forms.URLField, self).__init__(max_length, min_length, *args,
                                       **kwargs)
        self.validators.append(UniSubURLValidator(verify_exists=verify_exists, validator_user_agent=validator_user_agent))    