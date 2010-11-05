from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat as fs_format
from django.core import validators
from django.contrib.sites.models import Site

class MaxFileSizeValidator(object):
    
    def __init__(self, max_size, message=_(u'Please keep filesize under %(required_size)s. Current filesize %(current_size)s')):
        self.max_size = max_size
        self.message = message
        
    def __call__(self, content):
        if content._size > self.max_size:
            params = dict(required_size=fs_format(self.max_size), current_size=fs_format(content._size))
            raise ValidationError(self.message % params)
        
class UniSubURLValidator(validators.URLValidator):
    
    def __init__(self, verify_exists=False, validator_user_agent=validators.URL_VALIDATOR_USER_AGENT):
        self.host = Site.objects.get_current().domain
        super(UniSubURLValidator, self).__init__(verify_exists, validator_user_agent)
        
    def __call__(self, value):
        self.verify_exists = not value.startswith('http://'+self.host)
        super(UniSubURLValidator, self).__call__(value)