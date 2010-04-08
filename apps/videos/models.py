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
from datetime import datetime

NO_CAPTIONS, CAPTIONS_IN_PROGRESS, CAPTIONS_FINISHED = range(3)
VIDEO_TYPE_HTML5 = 'H'
VIDEO_TYPE_YOUTUBE = 'Y'
VIDEO_TYPE = (
    (VIDEO_TYPE_HTML5, 'HTML5'),
    (VIDEO_TYPE_YOUTUBE, 'Youtube')
)
WRITELOCK_EXPIRATION = 30 # 30 seconds
VIDEO_SESSION_KEY = 'video_session'

class Video(models.Model):
    video_id = models.CharField(max_length=255, unique=True)
    video_type = models.CharField(max_length=1, choices=VIDEO_TYPE)
    # only nonzero length for HTML5 videos
    video_url = models.URLField(max_length=2048)
    # only nonzero length for Youtube videos
    youtube_videoid = models.CharField(max_length=32)
    view_count = models.PositiveIntegerField(default=0)
    # the person who was first to start captioning this video.
    owner = models.ForeignKey(User, null=True)
    # always set to False for the time being.
    allow_community_edits = models.BooleanField()
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255)
    writelock_owner = models.ForeignKey(User, null=True, 
                                        related_name="writelock_owners")

    def __unicode__(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return 'html5: %s' % self.video_url
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            return 'youtube: %s' % self.youtube_videoid
        else:
            return 'unknown video %s' % video_url

    @property
    def srt_filename(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return '{0}.srt'.format(self.video_url.split('/')[-1])
        else:
            return 'youtube_{0}.srt'.format(self.youtube_videoid)

    @property
    def caption_state(self):
        video_captions = self.videocaptionversion_set.all()
        if len(video_captions) == 0:
            return NO_CAPTIONS
        if len(video_captions.filter(is_complete__exact=True)) > 0:
            return CAPTIONS_FINISHED
        else:
            return CAPTIONS_IN_PROGRESS

    def captions(self):
        """Returns latest VideoCaptionVersion, or None if no captions"""
        version_list = list(self.videocaptionversion_set.all())
        if len(version_list) == 0:
            return None
        else:
            return max(version_list, key=lambda v: v.version_no)

    def null_captions(self, user):
        captions = list(self.nullvideocaptions_set.all().filter(
                user__id__exact=user.id))
        return None if len(captions) == 0 else captions[0]

    def translation_language(self, language_code):
        """Returns a TranslationLanguage, or None if none found"""
        translations = list(self.translationlanguage_set.all().filter(
            language__exact=language_code))
        return None if len(translations) == 0 else translations[0]

    def captions_and_translations(self, language_code):
        """
        Returns (VideoCaption, Translation) tuple list, where the 
        Translation in each tuple might be None if there's no trans 
        for the caption
        """
        return self.make_captions_and_translations(
            self.captions(), self.translations(language_code))

    def null_captions_and_translations(self, user, language_code):
        """
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
        subtitles = list(subtitle_set.videocaption_set.all())
        translations = list(translation_set.translation_set.all())
        translations_dict = dict([(trans.caption_id, trans) for
                                  trans in translations])
        return [(subtitle,
                 None if subtitle.caption_id not in translations_dict
                 else translations_dict[subtitle.caption_id])
                for subtitle in subtitles]

    def translations(self, language_code):
        """Returns latest TranslationVersion, or None if none found"""
        trans_lang = self.translation_language(language_code)
        if trans_lang is None:
            return None
        return trans_lang.translations()

    def null_translations(self, user, language_code):
        translations = list(self.nulltranslations_set.all().filter(
                user__id__exact=user.id).filter(
                language__exact=language_code))
        return None if len(translations) == 0 else translations[0]

    def translation_language_codes(self):
        return set([trans.language for trans 
                    in list(self.translationlanguage_set.all())])

    def null_translation_language_codes(self, user):
        null_translations = list(
            self.nulltranslations_set.all().filter(
                user__id__exact=user.id))
        return set([trans.language for trans
                    in null_translations])

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

    def can_writelock(self, session_key):
        return self.writelock_session_key == session_key or \
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


def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    alphanum = string.letters+string.digits
    instance.video_id = ''.join([alphanum[random.randint(0, len(alphanum)-1)] 
                                                           for i in xrange(12)])
models.signals.pre_save.connect(create_video_id, sender=Video)

class VideoCaptionVersion(models.Model):
    video = models.ForeignKey(Video)
    version_no = models.PositiveIntegerField(default=0)
    # true iff user clicked "finish" at end of captioning process.
    is_complete = models.BooleanField()
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User)

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

    def can_writelock(self, session_key):
        return self.writelock_session_key == session_key or \
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
        version_list = list(self.translationversion_set.all())
        if len(version_list) == 0:
            return None
        else:
            return max(version_list, key=lambda v: v.version_no)


# TODO: make TranslationVersion unique on (video, version_no, language)
class TranslationVersion(models.Model):
    language = models.ForeignKey(TranslationLanguage)
    version_no = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User)
    # true iff user has clicked "finish" in translating process.
    is_complete = models.BooleanField()

# TODO: make Translation unique on (version, caption_id)
class Translation(models.Model):
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

class VideoCaption(models.Model):
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
