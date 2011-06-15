from statistic import st_sub_fetch_handler, st_video_view_handler, st_widget_view_statistic
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
        print '-----------------'
        
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
        print '-----------------'
        print 'Migrate videos view statistic'
        count = st_video_view_handler.migrate(verbosity=verbosity)
        print 'Videos view keys: ', count
        print '-----------------'
        print 'Migrate widget view statistic'
        count = st_widget_view_statistic.migrate(verbosity=verbosity)
        print 'Videos view keys: ', count        
