from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.conf.global_settings import LANGUAGES

class CustomUser(BaseUser):
    homepage = models.URLField(verify_exists=False, blank=True)
    preferred_language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)
    picture = models.ImageField(blank=True,
                                      upload_to='profile_images/%y/%m/')
    valid_email = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    biography = models.TextField('Tell us about yourself', blank=True)
    
    objects = UserManager()
        
    def __unicode__(self):
        return self.username
    
    @property
    def language(self):
        return self.get_preferred_language_display()