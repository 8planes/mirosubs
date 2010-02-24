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
    def caption_state(self):
        video_captions = self.videocaptionversion_set.all()
        if len(video_captions) == 0:
            return NO_CAPTIONS
        if len(video_captions.filter(is_complete__exact=True)) > 0:
            return CAPTIONS_FINISHED
        else:
            return CAPTIONS_IN_PROGRESS

    def translation(self, language_code):
        translations = list(self.translationlanguage_set.all().filter(
            language__exact=language_code))
        return None if len(translations) == 0 else translations[0]

    @property
    def translation_language_codes(self):
        return set([trans.language for trans 
                    in list(self.translationlanguage_set.all())])

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

    def last_video_caption_version(self):
        version_list = list(self.videocaptionversion_set.all())
        if len(version_list) == 0:
            return None
        else:
            return max(version_list, key=lambda v: v.version_no)


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
    # true iff user has gotten to "complete" part of captioning process.
    is_complete = models.BooleanField()
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User)


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


# TODO: make TranslationVersion unique on (video, version_no, language)
class TranslationVersion(models.Model):
    language = models.ForeignKey(TranslationLanguage)
    version_no = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User)

# TODO: make Translation unique on (version, caption_id)
class Translation(models.Model):
    version = models.ForeignKey(TranslationVersion)
    caption_id = models.IntegerField()
    translation_text = models.CharField(max_length=1024)

class VideoCaption(models.Model):
    version = models.ForeignKey(VideoCaptionVersion)
    caption_id = models.IntegerField()
    caption_text = models.CharField(max_length=1024)
    start_time = models.FloatField()
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
