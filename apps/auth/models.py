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
from django.db.models.signals import post_save
from django.conf import settings
import urllib
import hashlib
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.http import urlquote_plus
from django.core.exceptions import MultipleObjectsReturned
from utils.amazon import S3EnabledImageField
from datetime import datetime, date
from django.core.cache import cache

#I'm not sure this is the best way do do this, but this models.py is executed
#before all other and before url.py
from localeurl import patch_reverse
patch_reverse()

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

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
        max_length=16, choices=ALL_LANGUAGES, blank=True)
    picture = S3EnabledImageField(blank=True, upload_to='pictures/')
    valid_email = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    follow_new_video = models.BooleanField(default=True)
    biography = models.TextField('Tell us about yourself', blank=True)
    autoplay_preferences = models.IntegerField(
        choices=AUTOPLAY_CHOICES, default=AUTOPLAY_ON_BROWSER)
    award_points = models.IntegerField(default=0)
    last_ip = models.IPAddressField(blank=True, null=True)
    #videos witch are related to user. this is for quicker queries 
    videos = models.ManyToManyField('videos.Video', blank=True)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        
    def __unicode__(self):
        if not self.is_active:
            return ugettext('Retired user')
            
        if self.first_name:
            if self.last_name:
                return self.get_full_name()
            else:
                return self.first_name
        return self.username
    
    def unread_messages(self):
        from messages.models import Message
        
        return Message.objects.for_user(self).filter(read=False)
    
    @classmethod
    def video_followers_change_handler(cls, sender, instance, action, reverse, model, pk_set, **kwargs):
        from videos.models import SubtitleLanguage
        
        if reverse and action == 'post_add':
            #instance is User
            for video_pk in pk_set:
                cls.videos.through.objects.get_or_create(video__pk=video_pk, customuser=instance, defaults={'video_id': video_pk})
        elif reverse and action == 'post_remove':
            #instance is User
            for video_pk in pk_set:
                if not SubtitleLanguage.objects.filter(followers=instance, video__pk=video_pk).exists():
                    instance.videos.remove(video_pk)
        elif not reverse and action == 'post_add':
            #instance is Video
            for user_pk in pk_set:
                cls.videos.through.objects.get_or_create(video=instance, customuser__pk=user_pk, defaults={'customuser_id': user_pk})
        elif not reverse and action == 'post_remove':
            #instance is Video
            for user_pk in pk_set:
                if not SubtitleLanguage.objects.filter(followers__pk=user_pk, video=instance).exists():
                    instance.customuser_set.remove(user_pk)
        elif reverse and action == 'post_clear':
            #instance is User
            cls.videos.through.objects.filter(customuser=instance) \
                .exclude(video__subtitlelanguage__followers=instance).delete()
        elif not reverse and action == 'post_clear':
            #instance is Video
            cls.videos.through.objects.filter(video=instance) \
                .exclude(customuser__followed_languages__video=instance).delete()
            
    @classmethod
    def sl_followers_change_handler(cls, sender, instance, action, reverse, model, pk_set, **kwargs):
        from videos.models import Video, SubtitleLanguage
        
        if reverse and action == 'post_add':
            #instance is User
            for sl_pk in pk_set:
                sl = SubtitleLanguage.objects.get(pk=sl_pk)
                cls.videos.through.objects.get_or_create(video=sl.video, customuser=instance)
        elif reverse and action == 'post_remove':
            #instance is User
            for sl_pk in pk_set:
                if not Video.objects.filter(followers=instance, subtitlelanguage__pk=sl_pk).exists():
                    sl = SubtitleLanguage.objects.get(pk=sl_pk)
                    instance.videos.remove(sl.video)
        elif not reverse and action == 'post_add':
            #instance is SubtitleLanguage
            for user_pk in pk_set:
                cls.videos.through.objects.get_or_create(video=instance.video, customuser__pk=user_pk, defaults={'customuser_id': user_pk})
        elif not reverse and action == 'post_remove':
            #instance is SubtitleLanguage
            for user_pk in pk_set:
                if not Video.objects.filter(followers__pk=user_pk, subtitlelanguage=instance).exists():
                    instance.video.customuser_set.remove(user_pk)
        elif reverse and action == 'post_clear':
            #instance is User
            cls.videos.through.objects.filter(customuser=instance) \
                .exclude(video__subtitlelanguage__followers=instance).delete()
        elif not reverse and action == 'post_clear':
            #instance is SubtitleLanguage
            cls.videos.through.objects.filter(video=instance) \
                .exclude(customuser__followed_languages__video=instance.video).delete()
    
    def get_languages(self):
        """
        Just to control this query
        """
        languages = cache.get('user_languages_%s' % self.pk)

        if languages is None:
            languages = self.userlanguage_set.all()
            cache.set('user_languages_%s' % self.pk, languages, 60*24*7)

        return languages 

    def speaks_language(self, language_code):
        return language_code in [l.language for l in self.get_languages()]

    def managed_teams(self):
        from apps.teams.models import TeamMember
        return self.teams.filter(members__role=TeamMember.ROLE_MANAGER)

    def _get_gravatar(self, size):
        url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        url += urllib.urlencode({'d': 'mm', 's':str(size)})
        return url

    def _get_avatar_by_size(self, size):
        if self.picture:
            return self.picture.thumb_url(size, size)
        else:
            return self._get_gravatar(size)        
    
    def avatar(self):
        return self._get_avatar_by_size(100)

    def small_avatar(self):
        return self._get_avatar_by_size(50)
    
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
    def get_anonymous(cls):
        return cls.objects.get(pk=settings.ANONYMOUS_USER_ID)
    
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
        (1, _('understand enough')),
        (2, _('understand 99%')),
        (3, _('write like a native')),
    )
    user = models.ForeignKey(CustomUser)
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES, verbose_name='languages')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=1)
    follow_requests = models.BooleanField(verbose_name=_('follow requests in language'))

    class Meta:
        unique_together = ['user', 'language']

    def save(self, *args, **kwargs):
        super(UserLanguage, self).save(*args, **kwargs)
        cache.delete('user_languages_%s' % self.user_id)

    def delete(self, *args, **kwargs):
        cache.delete('user_languages_%s' % self.user_id)
        return super(UserLanguage, self).delete(*args, **kwargs)

class Announcement(models.Model):
    content = models.CharField(max_length=500)
    created = models.DateTimeField(help_text=_(u'This is date when start to display announcement. And only the last will be displayed.'))
    hidden = models.BooleanField(default=False)
    
    cache_key = 'last_accouncement'
    
    class Meta:
        ordering = ['-created']
    
    @classmethod
    def clear_cache(cls):
        cache.delete(cls.cache_key)
        
    def save(self, *args, **kwargs):
        super(Announcement, self).save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        self.clear_cache()
        return super(Announcement, self).delete(*args, **kwargs)
    
    @classmethod
    def last(cls):
        last = cache.get(cls.cache_key, '')

        if last == '':
            try:
                last = cls.objects.filter(created__lte=datetime.today()).filter(hidden=False)[0:1].get()
            except cls.DoesNotExist:
                last = None
            cache.set(cls.cache_key, last, 60*60)

        return last    
        
