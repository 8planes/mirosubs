from statistic.models import SubtitleFetchCounters
from statistic import sub_fetch_keys_set, changed_video_set
from utils.commands import ErrorHandlingCommand
from django.conf import settings
import sys
from utils.redis_utils import default_connection
from datetime import date
from videos.models import Video
from django.db.models import F

class Command(ErrorHandlingCommand):

    def handle(self, *args, **kwargs):
        print 'Start updating...'
        try:
            sub_fetch_keys_set.r.ping()
        except:
            if settings.DEBUG:
                raise
            print 'ERROR: Failed connect to Redis'
            self.handle_error(sys.exc_info())     
            return
        
        count = sub_fetch_keys_set.scard()
        
        print 'Subtitles fetch keys: ', count
        
        while count:
            count -= 1
            key = sub_fetch_keys_set.spop()
            
            if not key:
                break
            
            print 'Handle key: %s' % key
            
            parts = key.split(':')
            d = date(int(parts[-1]), int(parts[-2]), int(parts[-3]))
            
            if len(parts) == 6:
                lang = parts[2]
            else:
                lang = ''
            
            try:
                video = Video.objects.get(video_id=parts[1])
            except Video.DoesNotExist:
                print 'Video does not exist'
                default_connection.delete(key)
                continue
            
            counter_obj, created = SubtitleFetchCounters.objects.get_or_create(date=d, video=video, language=lang)
            counter_obj.count += int(default_connection.getset(key, 0))
            counter_obj.save()
            
        count = changed_video_set.scard()
        
        print 'Changed videos count: ', count
        
        while count:
            count -= 1

            video_id = changed_video_set.spop()

            if not video_id:
                break
            
            print 'Update statistic for video: %s' % video_id
            
            subtitles_fetched_counter = Video.subtitles_fetched_counter(video_id, True)
            widget_views_counter = Video.widget_views_counter(video_id, True)
            view_counter = Video.view_counter(video_id, True)
            
            Video.objects.filter(video_id=video_id).update(view_count=F('view_count')+view_counter.getset(0))
            Video.objects.update(widget_views_count=F('widget_views_count')+widget_views_counter.getset(0))
            Video.objects.update(subtitles_fetched_count=F('subtitles_fetched_count')+subtitles_fetched_counter.getset(0))