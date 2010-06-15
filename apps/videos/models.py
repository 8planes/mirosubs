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
import string
import random
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from django.db.models.signals import post_save
from django.utils.dateformat import format as date_format

NO_CAPTIONS, CAPTIONS_IN_PROGRESS, CAPTIONS_FINISHED = range(3)
VIDEO_TYPE_HTML5 = 'H'
VIDEO_TYPE_YOUTUBE = 'Y'
VIDEO_TYPE = (
    (VIDEO_TYPE_HTML5, 'HTML5'),
    (VIDEO_TYPE_YOUTUBE, 'Youtube')
)
WRITELOCK_EXPIRATION = 30 # 30 seconds
VIDEO_SESSION_KEY = 'video_session'

def format_time(time):
    t = int(time)
    s = t % 60
    s = s > 9 and s or '0%s' % s 
    return '%s:%s' % (t / 60, s)   

class Video(models.Model):
    """Central object in the system"""
    video_id = models.CharField(max_length=255, unique=True)
    video_type = models.CharField(max_length=1, choices=VIDEO_TYPE)
    # only nonzero length for HTML5 videos
    video_url = models.URLField(max_length=2048)
    # only nonzero length for Youtube videos
    youtube_videoid = models.CharField(max_length=32)
    youtube_name = models.CharField(max_length=2048, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    # the person who was first to start captioning this video.
    owner = models.ForeignKey(User, null=True)
    allow_community_edits = models.BooleanField()
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255)
    writelock_owner = models.ForeignKey(User, null=True, 
                                        related_name="writelock_owners")
    subtitles_fetched_count = models.IntegerField(default=0)
    widget_views_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return self.video_url
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            if self.youtube_name:
                return self.youtube_name
            return self.youtube_videoid
        else:
            return self.video_url 
    
    def get_video_url(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return self.video_url
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            return 'http://www.youtube.com/watch?v=%s' % self.youtube_videoid
        else:
            return self.video_url
        
    @property
    def srt_filename(self):
        """The best SRT filename for this video."""
        if self.video_type == VIDEO_TYPE_HTML5:
            return '{0}.srt'.format(self.video_url.split('/')[-1])
        else:
            return 'youtube_{0}.srt'.format(self.youtube_videoid)

    @property
    def caption_state(self):
        """Subtitling state for this video 

        Either subtitling hasn't started yet, or someone has marked one 
        VideoCaptionVersion as finished, or VideoCaptionVersions exist 
        but none have been marked as finished yet.
        """
        video_captions = self.videocaptionversion_set.all()
        if video_captions.count() == 0:
            return NO_CAPTIONS
        if video_captions.filter(is_complete__exact=True).count() > 0:
            return CAPTIONS_FINISHED
        else:
            return CAPTIONS_IN_PROGRESS

    def captions(self):
        """Returns latest VideoCaptionVersion, or None if no captions"""
        try:
            return self.videocaptionversion_set.order_by('-version_no')[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def null_captions(self, user):
        """Returns NullVideoCaptions for user, or None if none exist."""
        try:
            return self.nullvideocaptions_set.filter(
                user__id__exact=user.id)[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def translation_language(self, language_code):
        """Returns a TranslationLanguage, or None if none found"""
        try:
            return self.translationlanguage_set.filter(
                language__exact=language_code)[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def captions_and_translations(self, language_code):
        """(VideoCaption, Translation) pair list

        Returns (VideoCaption, Translation) tuple list, where the 
        Translation in each tuple might be None if there's no trans 
        for the caption
        """
        return self.make_captions_and_translations(
            self.captions(), self.translations(language_code))

    def null_captions_and_translations(self, user, language_code):
        """(VideoCaption, Translation) pair list

        Returns (VideoCaption, Translation) tuple list, where the 
        Translation in each tuple might be None if there's no trans 
        for the caption
        """
        return self.make_captions_and_translations(
            self.null_captions(user), 
            self.null_translations(user, language_code))

    def make_captions_and_translations(self, subtitle_set, translation_set):
        # FIXME: this should be private and static 
        # (no need for ref to self)
        subtitles = subtitle_set.videocaption_set.all()
        translations = translation_set.translation_set.all()
        translations_dict = dict([(trans.caption_id, trans) for
                                  trans in translations])
        return [(subtitle,
                 None if subtitle.caption_id not in translations_dict
                 else translations_dict[subtitle.caption_id])
                for subtitle in subtitles]

    def translations(self, language_code):
        """Returns latest TranslationVersion for language_code, or None if none found"""
        trans_lang = self.translation_language(language_code)
        if trans_lang is None:
            return None
        return trans_lang.translations()

    def null_translations(self, user, language_code):
        try:
            return self.nulltranslations_set.all().filter(
                user__id__exact=user.id).filter(
                language__exact=language_code)[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def translation_language_codes(self):
        """All iso language codes with translations."""
        return set([trans.language for trans 
                    in self.translationlanguage_set.all()])

    def null_translation_language_codes(self, user):
        null_translations = self.nulltranslations_set.filter(user__id__exact=user.id)
        return set([trans.language for trans in null_translations])

    @property
    def writelock_owner_name(self):
        """The user who currently has a subtitling writelock on this video."""
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.username

    @property
    def is_writelocked(self):
        """Is this video writelocked for subtitling?"""
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION

    def can_writelock(self, request):
        """Can I place a writelock on this video for subtitling?"""
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        """Writelock this video for subtitling."""
        if request.user.is_authenticated():
            self.writelock_owner = request.user
        else:
            self.writelock_owner = None
        self.writelock_session_key = request.session[VIDEO_SESSION_KEY]
        self.writelock_time = datetime.now()

    def release_writelock(self):
        """Writelock this video for subtitling."""
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None


def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    alphanum = string.letters+string.digits
    instance.video_id = ''.join([alphanum[random.randint(0, len(alphanum)-1)] 
                                                           for i in xrange(12)])
models.signals.pre_save.connect(create_video_id, sender=Video)

class VersionModel(models.Model):
    
    class Meta:
        abstract = True
        ordering = ['-datetime_started']
    
    def revision_time(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        d = self.datetime_started.date()
        if d == today:
            return 'Today'
        elif d == yesterday:
            return 'Yestarday'
        return d
    
    def time_change_display(self):
        if not self.time_change:
            return '0'
        else:
            return '%.0f%%' % (self.time_change*100)

    def text_change_display(self):
        if not self.text_change:
            return '0'
        else:
            return '%.0f%%' % (self.text_change*100)

class VideoCaptionVersion(VersionModel):
    """A video subtitles snapshot at the end of a particular subtitling session.

    A new VideoCaptionVersion is added during each subtitling session, each time 
    copying the subtitles from the previous session and adding any additional 
    changes for this session."""
    video = models.ForeignKey(Video)
    version_no = models.PositiveIntegerField(default=0)
    # true iff user clicked "finish" at end of captioning process.
    is_complete = models.BooleanField()
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User)
    note = models.CharField(max_length=512, blank=True)
    time_change = models.FloatField(null=True, blank=True)
    text_change = models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super(VideoCaptionVersion, self).save(*args, **kwargs)
        old_version = self.prev_version()
        new_captions = self.captions()
        captions_length = len(new_captions)

        if not old_version or not captions_length:
            #if it's first version set changes to 0
            self.time_change = 0
            self.text_change = 0
        else:
            old_captions = dict([(item.caption_id, item) for item in old_version.captions()])
            time_count_changed, text_count_changed = 0, 0
            #compare captions one by one and count changes in time and text
            for caption in new_captions:
                try:
                    old_caption = old_captions[caption.caption_id]
                    if not old_caption.caption_text == caption.caption_text:
                        text_count_changed += 1
                    if not old_caption.start_time == caption.start_time or \
                                    not old_caption.end_time == caption.end_time:
                        time_count_changed += 1
                except KeyError:
                    time_count_changed += 1
                    text_count_changed += 1
            self.time_change = time_count_changed / 1. / captions_length
            self.text_change = text_count_changed / 1. / captions_length   
        super(VideoCaptionVersion, self).save()
    
    def captions(self):
        return self.videocaption_set.order_by('start_time')

    def prev_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(datetime_started__lt=self.datetime_started) \
                      .filter(video=self.video)[:1].get()
        except models.ObjectDoesNotExist:
            pass
        
    def next_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(datetime_started__gt=self.datetime_started) \
                      .filter(video=self.video).order_by('datetime_started')[:1].get()
        except models.ObjectDoesNotExist:
            pass
    
    def rollback(self, user):
        cls = self.__class__
        latest_captions = self.video.captions()
        new_version_no = latest_captions.version_no + 1
        note = 'rollback to version #%s' % self.version_no
        new_version = cls(video=self.video, version_no=new_version_no, is_complete=True, \
            datetime_started=datetime.now(), user=user, note=note)
        new_version.save()
        for item in self.captions():
            item.duplicate_for(new_version).save()
        return new_version
                    
class NullVideoCaptions(models.Model):
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)
    # true iff user clicked "finish" at end of captioning process.
    is_complete = models.BooleanField()

class NullTranslations(models.Model):
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)
    language = models.CharField(max_length=16, choices=LANGUAGES)
    is_complete = models.BooleanField()

# TODO: make TranslationLanguage unique on (video, language)
class TranslationLanguage(models.Model):
    """A given language for a video.

    This object is writelocked whenever someone is editing translations 
    for a particular language for a particular video"""
    video = models.ForeignKey(Video)
    language = models.CharField(max_length=16, choices=LANGUAGES)
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255)
    writelock_owner = models.ForeignKey(User, null=True)

    # TODO: These methods are duplicated from Video, 
    # since they're both lockable. Fix the duplication.
    @property
    def writelock_owner_name(self):
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.username

    @property
    def is_writelocked(self):
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION

    def can_writelock(self, request):
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        if request.user.is_authenticated():
            self.writelock_owner = request.user
        else:
            self.writelock_owner = None
        self.writelock_session_key = request.session[VIDEO_SESSION_KEY]
        self.writelock_time = datetime.now()

    def release_writelock(self):
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None

    def translations(self):
        """Returns latest TranslationVersion, or None if none found"""
        try:
            return self.translationversion_set.order_by('-version_no')[:1].get()
        except models.ObjectDoesNotExist:
            pass

# TODO: make TranslationVersion unique on (video, version_no, language)
class TranslationVersion(VersionModel):
    """Snapshot of translations for a (video, language) pair at the end of a translating session.

    Every time a new translating session is started, the previous session's 
    translations are copied into a new TranslationVersion, and then the new 
    session works with the Translations attached to the new TranslationVersion.
    """
    language = models.ForeignKey(TranslationLanguage)
    version_no = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User)
    # true iff user has clicked "finish" in translating process.
    is_complete = models.BooleanField()
    datetime_started = models.DateTimeField()
    note = models.CharField(max_length=512, blank=True)
    time_change = models.FloatField(null=True, blank=True)
    text_change = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(TranslationVersion, self).save(*args, **kwargs)
        old_version = self.prev_version()
        new_captions = self.captions()
        captions_length = len(new_captions)
        
        self.time_change = 0
        if not old_version or not captions_length:
            #if it's first version set changes to 0
            self.text_change = 0
        else:
            old_captions = dict([(item.caption_id, item) for item in old_version.captions()])
            text_count_changed = 0
            #compare captions one by one and count changes in time and text
            for caption in new_captions:
                try:
                    old_caption = old_captions[caption.caption_id]
                    if not old_caption.translation_text == caption.translation_text:
                        text_count_changed += 1
                except KeyError:
                    text_count_changed += 1
            self.text_change = text_count_changed / 1. / captions_length   
        super(TranslationVersion, self).save()
    
    @property
    def video(self):
        return self.language.video
    
    def captions(self):
        return self.translation_set.all()

    def prev_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(datetime_started__lt=self.datetime_started) \
                      .filter(language=self.language)[:1].get()
        except models.ObjectDoesNotExist:
            pass
        
    def next_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(datetime_started__gt=self.datetime_started) \
                      .filter(language=self.language).order_by('datetime_started')[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def rollback(self, user):
        cls = self.__class__
        latest_captions = self.language.translations()
        new_version_no = latest_captions.version_no + 1
        note = 'rollback to version #%s' % self.version_no
        new_version = cls(language=self.language, version_no=new_version_no, is_complete=True, \
            datetime_started=datetime.now(), user=user, note=note)
        new_version.save()
        for item in self.captions():
            item.duplicate_for(new_version).save()
        return new_version
            
# TODO: make Translation unique on (version, caption_id)
class Translation(models.Model):
    """A translation of one subtitle.

    The subtitle to which this translation applies is identified by 
    caption_id. Using a foreign key would not work well on account 
    of the versioning system."""
    version = models.ForeignKey(TranslationVersion, null=True)
    null_translations = models.ForeignKey(NullTranslations, null=True)
    caption_id = models.IntegerField()
    translation_text = models.CharField(max_length=1024)

    def duplicate_for(self, new_version):
        return Translation(version=new_version,
                           caption_id=self.caption_id,
                           translation_text=self.translation_text)

    def update_from(self, translation_dict):
        self.translation_text = translation_dict['text']

    def to_json_dict(self):
        return { 'caption_id': self.caption_id,
                 'text': self.translation_text }
    
    def text(self):
        return self.translation_text

    @property
    def caption(self):
        #cache caption for self.caption_id
        if not hasattr(self, '_caption'):
            try:
                c = VideoCaption.objects.filter(caption_id=self.caption_id) \
                        .order_by('-version__datetime_started')[:1].get()        
            except VideoCaption.DoesNotExist:
                c = None
            setattr(self, '_caption', c)
        return self._caption
    
    def display_time(self):
        return self.caption and format_time(self.caption.start_time) or ''   

    def display_end_time(self):
        return self.caption and format_time(self.caption.end_time) or ''   
    
class VideoCaption(models.Model):
    """A single subtitle for a video.

    Note that caption_id is an identifier that is assigned by the client 
    while subtitling. caption_id should be unique for each VideoCaption 
    for a given video. caption_id remains the same across VideoCaptionVersions, 
    unlike database primary keys."""
    version = models.ForeignKey(VideoCaptionVersion, null=True)
    null_captions = models.ForeignKey(NullVideoCaptions, null=True)
    caption_id = models.IntegerField()
    caption_text = models.CharField(max_length=1024)
    # in seconds
    start_time = models.FloatField()
    # in seconds
    end_time = models.FloatField()

    def duplicate_for(self, new_version):
        return VideoCaption(version=new_version,
                            caption_id=self.caption_id,
                            caption_text=self.caption_text,
                            start_time=self.start_time,
                            end_time=self.end_time)

    def update_from(self, caption_dict):
        self.caption_text = caption_dict['caption_text']
        self.start_time = caption_dict['start_time']
        self.end_time = caption_dict['end_time']

    def to_json_dict(self, text_to_use=None):
        text = self.caption_text if text_to_use is None else text_to_use
        return { 'caption_id' : self.caption_id, 
                 'caption_text' : text, 
                 'start_time' : self.start_time, 
                 'end_time' : self.end_time }       
    
    def display_time(self):
        return format_time(self.start_time)
    
    def display_end_time(self):
        if self.end_time == 99999:
            return 'END'
        return format_time(self.end_time)
    
    def text(self):
        return self.caption_text
    
class Action(models.Model):
    TYPE_CHOICES = (
        (1, 'subtitles'),
        (2, 'translations')
    )
    user = models.ForeignKey(User)
    video = models.ForeignKey(Video)
    language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)
    created = models.DateTimeField()
    
    class Meta:
        ordering = ['-created']
        get_latest_by = 'created'
    
    def time(self):
        if self.created.date() == date.today():
            format = 'g:i A'
        else:
            format = 'g:i A, j M Y'
        return date_format(self.created, format)           
    
    def uprofile(self):
        try:
            return self.user.profile_set.all()[0]
        except IndexError:
            pass        
    
    @classmethod
    def create_translation_handler(cls, sender, instance, created, **kwargs):
        if created:
            video = instance.language.video
            user = instance.user
            language = instance.language.language
            
            try:
                la = cls.objects.latest()
                if la.user == user and la.video == video and la.language == language:
                    la.created = instance.datetime_started
                    la.save()
                    return
            except cls.DoesNotExist:
                pass
            
            obj = cls(user=user, video=video)
            obj.language = language
            obj.created = instance.datetime_started
            obj.save()
    
    @classmethod
    def create_caption_handler(cls, sender, instance, created, **kwargs):
        if created:
            user = instance.user
            video = instance.video

            try:
                la = cls.objects.latest()
                if la.user == user and la.video == video:
                    la.created = instance.datetime_started
                    la.save()                    
                    return
            except cls.DoesNotExist:
                pass
                       
            obj = cls(user=user, video=video)
            obj.created = instance.datetime_started
            obj.save()            
        
post_save.connect(Action.create_translation_handler, TranslationVersion)
post_save.connect(Action.create_caption_handler, VideoCaptionVersion)

class UserTestResult(models.Model):
    email = models.EmailField()
    browser = models.CharField(max_length=1024)
    task1 = models.TextField()
    task2 = models.TextField(blank=True)
    task3 = models.TextField(blank=True)
    get_updates = models.BooleanField(default=False)
