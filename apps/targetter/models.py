from django.db import models
from targetter import BROWSER_DICT, OS_DICT
from django.utils.translation import ugettext_lazy as _

class MessageConfig(models.Model):
    message = models.TextField()
    os = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    browser = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    top_latitude = models.FloatField(blank=True, null=True)
    top_longitude = models.FloatField(blank=True, null=True)
    side_length = models.FloatField(blank=True, null=True, help_text=_(u'in degrees'))
    
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
        
        config['top_latitude'] = self.top_latitude
        config['top_longitude'] = self.top_longitude
        config['side_length'] = self.side_length
        
        return config            