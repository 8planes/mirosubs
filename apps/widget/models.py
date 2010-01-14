from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User

class Video(models.Model):
    video_id = models.CharField(max_length=255)
    video_url = models.CharField(max_length=2048, unique=True)
    view_count = models.PositiveIntegerField(default=0)
    # the person who was first to start captioning this video.
    owner = models.ForeignKey(User)
    # always set to False for the time being.
    allow_community_edits = models.BooleanField()
    writelock_time = models.DateTimeField(null=True)
    writelock_owner = models.ForeignKey(User, null=True, related_name='writelock_owners')

    def __unicode__(self):
        return self.video_url

def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    instance.video_id = str(uuid4())
models.signals.pre_save.connect(create_video_id, sender=Video)

class VideoCaptionVersion(models.Model):
    video = models.ForeignKey(Video)
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
