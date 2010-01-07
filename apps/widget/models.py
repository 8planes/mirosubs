from django.db import models

class Video(models.Model):
    video_url = models.CharField(max_length=2048)

class VideoCaption(models.Model):
    video = models.ForeignKey(Video)
    caption_id = models.IntegerField()
    caption_text = models.CharField(max_length=1024)
    start_time = models.FloatField()
    end_time = models.FloatField()
