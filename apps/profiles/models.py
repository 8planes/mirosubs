from django.db import models
from django.contrib.auth.models import User
import registration.signals
from django.contrib.auth import login, authenticate


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
    valid_email = models.BooleanField(default=False)
        
    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

def create_profile(sender, instance, **kwargs):
    if not instance:
        return
    profile, created = Profile.objects.get_or_create(user=instance)
models.signals.post_save.connect(create_profile, sender=User)


# The registration module is only being used to check emails. These two
#functions ensure that the user is active immediately after registering and that
# profile.valid_email reflects whether the user has verified her email.
def register_user(sender, user, request, **kwargs):
    if not user:
        return
    user.is_active = True
    user.save()
    u = authenticate(username=request.POST.get('username'),
                     password=request.POST.get('password1'))
    if u is not None:
        login(request, u)
registration.signals.user_registered.connect(register_user)

def activate_user(sender, user, request, **kwargs):
    if not user:
        return
    profile = user.get_profile()
    profile.valid_email = True
    profile.save()
registration.signals.user_activated.connect(activate_user)