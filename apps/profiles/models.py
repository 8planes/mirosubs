# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.db import models
from django.contrib.auth.models import User
import registration.signals
from django.contrib.auth import login, authenticate
from django.conf.global_settings import LANGUAGES

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    homepage = models.URLField(verify_exists=False, blank=True)
    preferred_language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)
    picture = models.ImageField(blank=True,
                                      upload_to='profile_images/%y/%m/')
    valid_email = models.BooleanField(default=False)
        
    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    
    @property
    def language(self):
        return self.get_preferred_language_display()
    
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