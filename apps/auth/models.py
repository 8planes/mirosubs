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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.conf.global_settings import LANGUAGES
from django.db.models.signals import post_save
from django.conf import settings
import hashlib
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote_plus
from django.core.exceptions import MultipleObjectsReturned
from utils.amazon.thumbnail import AmazonThumbnail
from utils.amazon import S3EnabledImageField

SORTED_LANGUAGES = list(LANGUAGES)
SORTED_LANGUAGES.sort(key=lambda item: item[1])

class CustomUser(BaseUser):
    AUTOPLAY_ON_BROWSER = 1
    AUTOPLAY_ON_LANGUAGES = 2
    DONT_AUTOPLAY = 3
    AUTOPLAY_CHOICES = (
        (AUTOPLAY_ON_BROWSER, 
         'Autoplay subtitles based on browser preferred languages'),
        (AUTOPLAY_ON_LANGUAGES, 'Autoplay subtitles in languages I know'),
        (DONT_AUTOPLAY, 'Don\'t autoplay subtitles')
    )
    homepage = models.URLField(verify_exists=False, blank=True)
    preferred_language = models.CharField(
        max_length=16, choices=SORTED_LANGUAGES, blank=True)
    picture = S3EnabledImageField(blank=True, upload_to='pictures/')
    valid_email = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    biography = models.TextField('Tell us about yourself', blank=True)
    autoplay_preferences = models.IntegerField(
        choices=AUTOPLAY_CHOICES, default=AUTOPLAY_ON_BROWSER)
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
    
    def avatar(self):
        return self.picture.thumb_url(128, 128)
    
    @models.permalink
    def get_absolute_url(self):
        return ('profiles:profile', [urlquote_plus(self.username)])
    
    @property
    def language(self):
        return self.get_preferred_language_display()
    
    @models.permalink
    def profile_url(self):
        return ('profiles:profile', [self.pk])
    
    def hash_for_video(self, video_id):
        return hashlib.sha224(settings.SECRET_KEY+str(self.pk)+video_id).hexdigest()
    
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
    EDIT_SUBTITLES = 4
    EDIT_TRANSLATION = 5
    RATING = 6
    TYPE_CHOICES = (
        (COMMENT, _(u'Add comment')),
        (START_SUBTITLES, _(u'Start subtitles')),
        (START_TRANSLATION, _(u'Start translation')),
        (EDIT_SUBTITLES, _(u'Edit subtitles')),
        (EDIT_TRANSLATION, _(u'Edit translation'))
    )
    points = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    user = models.ForeignKey(CustomUser, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def _set_points(self):
        if self.type == self.COMMENT:
            self.points = 10
        elif self.type == self.START_SUBTITLES:
            self.points = 100
        elif self.type == self.START_TRANSLATION:
            self.points = 100
        elif self.type == self.EDIT_SUBTITLES:
            self.points = 50
        elif self.type == self.EDIT_TRANSLATION:
            self.points = 50
        else:
            self.points = 0
        
    def save(self, *args, **kwrags):
        self.points or self._set_points()
        if not self.pk:
            CustomUser.objects.filter(pk=self.user.pk).update(award_points=models.F('award_points')+self.points)
        return super(Awards, self).save(*args, **kwrags)
    
    @classmethod
    def on_comment_save(cls, sender, instance, created, **kwargs):
        if created:
            try:
                cls.objects.get_or_create(user=instance.user, type = cls.COMMENT)
            except MultipleObjectsReturned:
                pass
            
    @classmethod
    def on_subtitle_version_save(cls, sender, instance, created, **kwargs):
        if not instance.user:
            return
        
        if created and instance.version_no == 0:
            if instance.language.is_original:
                type = cls.START_SUBTITLES
            else:
                type = cls.START_TRANSLATION
        else:
            if instance.language.is_original:
                type = cls.EDIT_SUBTITLES
            else:
                type = cls.EDIT_TRANSLATION
        try:
            cls.objects.get_or_create(user=instance.user, type=type)
        except MultipleObjectsReturned:
            pass
    
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
