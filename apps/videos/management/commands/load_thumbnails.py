from utils.commands import ErrorHandlingCommand
from django.conf import settings
from utils.amazon import default_s3_store
from videos.models import Video, VIDEO_TYPE_FLV, VIDEO_TYPE_HTML5
import urllib
import os
import commands
import sys
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.db.models import ObjectDoesNotExist

VIDEO_UPLOAD_PATH = getattr(settings, 'VIDEO_UPLOAD_PATH', \
                            os.path.join(settings.MEDIA_ROOT, 'videos'))

VIDEO_THUMBNAILS_FOLDER = getattr(settings, 'VIDEO_THUMBNAILS_PATH', 'videos/thumbnails/')

THUMBNAILS_PATH = os.path.join(settings.MEDIA_ROOT, VIDEO_THUMBNAILS_FOLDER) 

class Command(ErrorHandlingCommand):
    
    def handle(self, *args, **options):
        print 'Run load thumbnail command'
        self.verbosity = int(options.get('verbosity', 1))
        self.s3_store = self.init_s3()
        
        if not os.path.exists(VIDEO_UPLOAD_PATH):
            os.makedirs(VIDEO_UPLOAD_PATH)
        
        if not os.path.exists(THUMBNAILS_PATH):
            os.makedirs(THUMBNAILS_PATH)
            
        qs = Video.objects.filter(thumbnail='', videourl__original=True, videourl__type__in=[VIDEO_TYPE_FLV, VIDEO_TYPE_HTML5])
        
        for video in qs:
            self.print_to_console(u'Handling %s' % video.__unicode__())

            try:
                video_url = video.videourl_set.filter(original=True)[:1].get()
            except ObjectDoesNotExist:
                continue    
            
            path = self.get_file_path(video, video_url)

            if not os.path.exists(path):
                self.print_to_console(u'Saving...')
                urllib.urlretrieve(video_url.url, path)
                self.print_to_console(u'Video saved.')
            else:
                self.print_to_console(u'File exist.')
            
            self.get_thumbnail(video, path)
                
            self.print_to_console(u'-----------------')
        
        #--- Save original thumbnails to S3 Store ---
        self.print_to_console(u'Save original thumbnails to S3 Store...')
        
        qs = Video.objects.exclude(thumbnail='').filter(s3_thumbnail='')
        for video in qs:
            self.print_to_console(u'Handling %s' % video.__unicode__())
            
            name = video.thumbnail.strip('/').split('/')[-1]
            cf = ContentFile(urllib.urlopen(video.thumbnail).read())
            video.s3_thumbnail.save('%s/%s' % (video.video_id, name), cf, True)
        
    def init_s3(self):
        if not default_s3_store:
            raise ImproperlyConfigured('Have not settings for thumbnails uploading to S3 Store.')
        return default_s3_store
        
    def get_thumbnail(self, video, path):
        self.print_to_console(u'Get thumbnail...')
        
        grabimage = "ffmpeg -y -i %s -vframes 1 -ss 00:00:%s -an -vcodec png -f rawvideo  %s"
        
        thumbnailfilename = "%s.png" % video.video_id
        thumbnailpath = os.path.normpath(os.path.join(THUMBNAILS_PATH, thumbnailfilename))
        
        grab_result = 'Command is not runned yet'
        try:
            grab_result = commands.getoutput(grabimage % (path, 10, thumbnailpath))
            if not os.path.exists(thumbnailpath):
                raise Exception('Error in converting: %s' % grab_result)
            if not os.path.getsize(thumbnailpath):
                grab_result = commands.getoutput(grabimage % (path, 5, thumbnailpath))
                
            self.print_to_console(u'Saving in S3 Store...')
            cf = ContentFile(open(thumbnailpath, 'rb').read())
            video.s3_thumbnail.save(thumbnailfilename, cf, True)
            video.thumbnail = video.s3_thumbnail.url
            video.save()
            os.remove(thumbnailpath)
            os.remove(path)
        except:
            if settings.DEBUG:
                raise
            self.handle_error(sys.exc_info())         
        
    def get_file_path(self, video, video_url):
        type = video_url.url.split('.')[-1]
        name = '%s.%s' % (video.video_id, type)
        return os.path.join(VIDEO_UPLOAD_PATH, name)    
        