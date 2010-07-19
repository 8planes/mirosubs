from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.conf.global_settings import LANGUAGES

class CustomUser(BaseUser):
    AUTOPLAY_ON_BROWSER = 1
    AUTOPLAY_ON_LANGUAGES = 2
    DONT_AUTOPLAY = 3
    AUTOPLAY_CHOICES = (
        (AUTOPLAY_ON_BROWSER, 'Autoplay subtitles based on browser preferred languages'),
        (AUTOPLAY_ON_LANGUAGES, 'Autoplay subtitles in languages I know'),
        (DONT_AUTOPLAY, 'Don\'t autoplay subtitles')
    )
    homepage = models.URLField(verify_exists=False, blank=True)
    preferred_language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)
    picture = models.ImageField(blank=True,
                                      upload_to='profile_images/%y/%m/')
    valid_email = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    biography = models.TextField('Tell us about yourself', blank=True)
    autoplay_preferences = models.IntegerField(choices=AUTOPLAY_CHOICES, default=AUTOPLAY_ON_BROWSER)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        
    def __unicode__(self):
        return self.username
    
    @property
    def language(self):
        return self.get_preferred_language_display()
    
    @models.permalink
    def profile_url(self):
        return ('profiles:profile', [self.pk])

    def _get_unique_checks(self, exclude=None):
        #add email field validate like unique
        unique_checks, date_checks = super(CustomUser, self)._get_unique_checks(exclude)
        unique_checks.append((CustomUser, ('email',)))
        return unique_checks, date_checks
    
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