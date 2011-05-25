from statistic import changed_video_set, st_sub_fetch_handler, st_video_view_handler 
from utils.commands import ErrorHandlingCommand
from django.conf import settings
import sys
from utils.redis_utils import default_connection
from videos.models import Video
from django.db.models import F

class Command(ErrorHandlingCommand):

    def handle(self, *args, **kwargs):
        verbosity = kwargs.get('verbosity', 1)
        print 'Start updating...'
        
        try:
            default_connection.ping()
        except:
            if settings.DEBUG:
                raise
            print 'ERROR: Failed connect to Redis'
            self.handle_error(sys.exc_info())     
            return
        
        print 'Migrate subtitles fetch statistic'
        count = st_sub_fetch_handler.migrate(verbosity=verbosity)
        print 'Subtitles fetch keys: ', count

        print 'Migrate videos view statistic'
        count = st_video_view_handler.migrate(verbosity=verbosity)
        print 'Videos view keys: ', count
            
        count = changed_video_set.scard()
        
        print 'Changed videos count: ', count
        
        while count:
            count -= 1

            video_id = changed_video_set.spop()

            if not video_id:
                break
            
            print 'Update statistic for video: %s' % video_id
            
            subtitles_fetched_counter = Video.subtitles_fetched_counter(video_id, skip_mark_as_changed=True)
            widget_views_counter = Video.widget_views_counter(video_id, skip_mark_as_changed=True)
            view_counter = Video.view_counter(video_id, skip_mark_as_changed=True)

            Video.objects.filter(video_id=video_id).update(view_count=F('view_count')+view_counter.getset(0))
            Video.objects.filter(video_id=video_id).update(widget_views_count=F('widget_views_count')+widget_views_counter.getset(0))
            Video.objects.filter(video_id=video_id).update(subtitles_fetched_count=F('subtitles_fetched_count')+subtitles_fetched_counter.getset(0))