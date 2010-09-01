from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.conf.global_settings import LANGUAGES
from django.db.models.signals import post_save
from django.conf import settings
import sha
from django.utils.translation import ugettext_lazy as _

SORTED_LANGUAGES = list(LANGUAGES)
SORTED_LANGUAGES.sort(key=lambda item: item[1])

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
    preferred_language = models.CharField(max_length=16, choices=SORTED_LANGUAGES, blank=True)
    picture = models.ImageField(blank=True,
                                      upload_to='profile_images/%y/%m/')
    valid_email = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    biography = models.TextField('Tell us about yourself', blank=True)
    autoplay_preferences = models.IntegerField(choices=AUTOPLAY_CHOICES, default=AUTOPLAY_ON_BROWSER)
    award_points = models.IntegerField(default=0)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        
    def __unicode__(self):
        if self.first_name:
            if self.last_name:
                return self.get_full_name()
            else:
                return self.first_name
        return self.username
    
    @property
    def language(self):
        return self.get_preferred_language_display()
    
    @models.permalink
    def profile_url(self):
        return ('profiles:profile', [self.pk])
    
    def hash_for_video(self, video_id):
        return sha.new(settings.SECRET_KEY+str(self.pk)+video_id).hexdigest()
    
    def _get_unique_checks(self, exclude=None):
        #add email field validate like unique
        unique_checks, date_checks = super(CustomUser, self)._get_unique_checks(exclude)
        unique_checks.append((CustomUser, ('email',)))
        return unique_checks, date_checks
    
    @classmethod
    def get_youtube_anonymous(cls):
        return cls.objects.get(pk=10000)
    
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = CustomUser(**values)
        user.save()
        
post_save.connect(create_custom_user, BaseUser)

class Awards(models.Model):
    COMMENT = 1
    START_SUBTITLES = 2
    START_TRANSLATION = 3
    TYPE_CHOICES = (
        (COMMENT, _(u'Add comment')),
        (START_SUBTITLES, _(u'Start subtitles')),
        (START_TRANSLATION, _(u'Start translation'))
    )
    points = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    user = models.ForeignKey(CustomUser)
    created = models.DateTimeField(auto_now_add=True)
    
    def _set_points(self):
        if self.type == self.COMMENT:
            self.points = 10
        elif self.type == self.START_SUBTITLES:
            self.points = 100
        elif self.type == self.START_TRANSLATION:
            self.points = 100    
        
    def save(self, *args, **kwrags):
        self.points or self._set_points()
        if not self.pk:
            CustomUser.objects.filter(pk=self.user.pk).update(award_points=models.F('award_points')+self.points)
        return super(Awards, self).save(*args, **kwrags)
    
    @classmethod
    def on_comment_save(cls, sender, instance, created, **kwargs):
        if created:
            obj = cls(user=instance.user, type = cls.COMMENT)
            obj.save()
    
class UserLanguage(models.Model):
    PROFICIENCY_CHOICES = (
        (1, 'understand enough'),
        (2, 'understand 99%'),
        (3, 'write like a native'),
    )
    user = models.ForeignKey(CustomUser)
    language = models.CharField(max_length=16, choices=SORTED_LANGUAGES, verbose_name='languages')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES)
    
    class Meta:
        unique_together = ['user', 'language']