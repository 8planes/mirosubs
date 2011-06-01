from django.core.management.base import BaseCommand
from videos.models import VideoFeed
from videos.tasks import update_video_feed

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print 'Run update_from_feed command'
        
        for feed in VideoFeed.objects.all():
            print '-------------------------'
            print feed.url
            update_video_feed.delay(feed.pk)