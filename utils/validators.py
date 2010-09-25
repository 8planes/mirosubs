from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat as fs_format

class MaxFileSizeValidator(object):
    
    def __init__(self, max_size, message=_(u'Please keep filesize under %s. Current filesize %s')):
        self.max_size = max_size
        self.message = message
        
    def __call__(self, content):
        if content._size > self.max_size:
            raise ValidationError(self.message % (fs_format(self.max_size), fs_format(content._size)))