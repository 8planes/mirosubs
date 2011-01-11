from django.db import models
from targetter import BROWSER_DICT, OS_DICT

class MessageConfig(models.Model):
    message = models.TextField()
    os = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    browser = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=200)
    
    @models.permalink
    def get_absolute_url(self):
        return ('targetter:test', [self.pk])
    
    def get_config(self):
        config = {
            'text': self.message
        }
        
        if self.os:
            config['os'] = [OS_DICT.get(int(i), '') for i in self.os.split(',')]
            
        if self.os:
            config['userAgents'] = [BROWSER_DICT.get(int(i), '') for i in self.browser.split(',')]
            
        return config            