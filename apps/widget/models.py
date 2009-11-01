from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User
from datetime import datetime

NO_CAPTIONS, CAPTIONS_IN_PROGRESS, CAPTIONS_FINISHED = range(3)
WRITELOCK_EXPIRATION = 120 # 2 minutes

class Video(models.Model):
    video_id = models.CharField(max_length=255, unique=True)
    video_url = models.URLField(max_length=2048, unique=True)
    view_count = models.PositiveIntegerField(default=0)
    # the person who was first to start captioning this video.
    owner = models.ForeignKey(User, null=True)
    # always set to False for the time being.
    allow_community_edits = models.BooleanField()
    writelock_time = models.DateTimeField(null=True)
    writelock_owner = models.ForeignKey(User, null=True, related_name='writelock_owners')

    def __unicode__(self):
        return self.video_url

    @property
    def caption_state(self):
        video_captions = self.videocaptionversion_set.all()
        if len(video_captions) == 0:
            return NO_CAPTIONS
        if len(video_captions.filter(is_complete__exact=True)) > 0:
            return CAPTIONS_FINISHED
        else:
            return CAPTIONS_IN_PROGRESS

    @property
    def is_writelocked(self):
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION

    def can_writelock(self, user):
        if user != None and \
           (self.writelock_owner == None or \
            self.writelock_owner == user or \
            not self.is_writelocked):
            return True
        if user == None and (self.writelock_owner == None or not self.is_writelocked):
            return True
        return False

def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    instance.video_id = str(uuid4())
models.signals.pre_save.connect(create_video_id, sender=Video)

class VideoCaptionVersion(models.Model):
    video = models.ForeignKey(Video)
    version_no = models.PositiveIntegerField(default=0)
    # true iff all captions have beg & end time values assigned.
    is_complete = models.BooleanField()
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User)

class VideoCaption(models.Model):
    version = models.ForeignKey(VideoCaptionVersion)
    caption_id = models.IntegerField()
    caption_text = models.CharField(max_length=1024)
    start_time = models.FloatField()
    end_time = models.FloatField()
