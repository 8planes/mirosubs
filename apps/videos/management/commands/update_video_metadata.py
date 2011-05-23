from django.core.management.base import BaseCommand
from apps.videos.models import Video
from apps.videos.metadata_manager import update_metadata
from time import sleep
import sentry_logger                
import logging 
logger = logging.getLogger(__name__)
import sys
from time import sleep

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print 'Run update_metadata command'
        targets = Video.objects.all()
        percent_printed = 0
        num = targets.count()
        count = 0
        print "%s videos to go " % num
        must_return = False
        for x in targets.iterator():
            try:
                update_metadata(x.pk)
                percent = "%.2f %%" % (((count * 1.0) / num) * 100)
                count +=1          
                if percent > percent_printed:
                    percent_printed = percent
                    print "Done %s%%" % (percent)
            except (KeyboardInterrupt, SystemExit):
                must_return = True
                print "stopped at %s" % count
            except:
                print "failed for pk %s"  % x.pk
                logger.exception("metadata import")
            if must_return:
                return
            sleep(0.2)
