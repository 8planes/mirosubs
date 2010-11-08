from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from utils.amazon import default_s3_store
from videos.models import Video, VIDEO_TYPE_FLV, VIDEO_TYPE_HTML5
import urllib
import os
from django.core.mail import mail_admins
import commands
import sys
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile

VIDEO_UPLOAD_PATH = getattr(settings, 'VIDEO_UPLOAD_PATH', \
                            os.path.join(settings.MEDIA_ROOT, 'videos'))

VIDEO_THUMBNAILS_FOLDER = getattr(settings, 'VIDEO_THUMBNAILS_PATH', 'videos/thumbnails/')

THUMBNAILS_PATH = os.path.join(settings.MEDIA_ROOT, VIDEO_THUMBNAILS_FOLDER) 

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.s3_store = self.init_s3()
        
        if not os.path.exists(VIDEO_UPLOAD_PATH):
            os.makedirs(VIDEO_UPLOAD_PATH)
        
        if not os.path.exists(THUMBNAILS_PATH):
            os.makedirs(THUMBNAILS_PATH)
            
        qs = Video.objects.filter(thumbnail='', video_type__in=[VIDEO_TYPE_FLV, VIDEO_TYPE_HTML5])
        
        for video in qs:
            self.print_to_console(u'Handling %s' % video.__unicode__())
            
            path = self.get_file_path(video)
            if not os.path.exists(path):
                self.print_to_console(u'Saving...')
                urllib.urlretrieve(video.video_url, path)
                self.print_to_console(u'Video saved.')
            else:
                self.print_to_console(u'File exist.')
            
            self.get_thumbnail(video, path)
                
            self.print_to_console(u'-----------------')
    
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
                raise Exception('Error in converting')
            if not os.path.getsize(thumbnailpath):
                grab_result = commands.getoutput(grabimage % (path, 5, thumbnailpath))
                
            self.print_to_console(u'Saving in S3 Store...')
            self.s3_store.save(VIDEO_THUMBNAILS_FOLDER+thumbnailfilename, ContentFile(open(thumbnailpath, 'rb').read()))
            
            video.thumbnail = VIDEO_THUMBNAILS_FOLDER+thumbnailfilename
            video.save()
            os.remove(thumbnailpath)
            os.remove(path)
        except:
            if settings.DEBUG:
                raise
            self.handle_error(video, grab_result, sys.exc_info())         
    
    def handle_error(self, video, command_msg, exc_info):
        subject = u'Error during thumbnail grabing for video: %s' % video.video_id
        message = "%s\n\n%s" % (self._get_traceback(exc_info),command_msg)
        mail_admins(subject, message, fail_silently=False)

    def _get_traceback(self, exc_info=None):
        "Helper function to return the traceback as a string"
        import traceback
        return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))            
        
    def get_file_path(self, video):
        type = video.video_url.split('.')[-1]
        name = '%s.%s' % (video.video_id, type)
        return os.path.join(VIDEO_UPLOAD_PATH, name)
    
    def print_to_console(self, msg, min_verbosity=1):
        if self.verbosity >= min_verbosity:
            print msg