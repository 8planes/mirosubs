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
    
    @models.permalink
    def profile_url(self):
        return ('profiles:profile', [self.pk])
    
class UserLanguage(models.Model):
    PROFICIENCY_CHOICES = (
        (1, 'knowpretty well'),
        (2, 'understand 99%'),
        (3, 'can translate into this language'),
    )
    user = models.ForeignKey(CustomUser)
    language = models.CharField(max_length=16, choices=LANGUAGES, verbose_name='languages')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES)
    
    class Meta:
        unique_together = ['user', 'language']