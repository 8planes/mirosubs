from django.db import models
from uuid import uuid4

class Video(models.Model):
    video_id = models.CharField(max_length=255)
    video_url = models.CharField(max_length=2048)

def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    instance.video_id = str(uuid4())
models.signals.pre_save.connect(create_video_id, sender=Video)
    

class VideoCaption(models.Model):
    video = models.ForeignKey(Video)
    caption_id = models.IntegerField()
    caption_text = models.CharField(max_length=1024)
    start_time = models.FloatField()
    end_time = models.FloatField()
