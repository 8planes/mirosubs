from django.db import models
from targetter import BROWSER_DICT, OS_DICT
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class MessageConfig(models.Model):
    message = models.TextField()
    os = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    browser = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    center_latitude = models.FloatField(blank=True, null=True)
    center_longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True, help_text=_(u'in miles'))
    
    def __unicode__(self):
        return self.message[:50]
    
    @models.permalink
    def get_absolute_url(self):
        return ('targetter:test', [self.pk])
    
    def get_config(self):
        config = {
            'text': self.message
        }
        
        if self.os:
            config['os'] = [OS_DICT.get(int(i), '') for i in self.os.split(',') if i != '']
            
        if self.os:
            config['userAgents'] = [BROWSER_DICT.get(int(i), '') for i in self.browser.split(',') if i != '']
        
        config['center_latitude'] = self.center_latitude
        config['center_longitude'] = self.center_longitude
        config['radius'] = self.radius
        
        return config            