from django.db import models
from django.contrib.auth.models import User

class Language(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    homepage = models.URLField(verify_exists=False, blank=True)
    preferred_language = models.ForeignKey(Language, blank=True, null=True)
    picture = models.ImageField(blank=True,
                                      upload_to='profile_images/%y/%m/')
        
    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

def create_profile(sender, instance, **kwargs):
    if not instance:
        return
    profile, created = Profile.objects.get_or_create(user=instance)
models.signals.post_save.connect(create_profile, sender=User)