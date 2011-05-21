from django.core.management.base import BaseCommand
from apps.videos.models import Video
from apps.videos.metadata_manager import update_metadata

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print 'Run update_metadata command'
        targets = Video.objects.all()
        percent_printed = 0
        num = targets.count()
        count = 0
        print "%s videos to go " % num
        for x in targets.iterator():
            try:
                update_metadata(x.pk)
                percent = "%.2f %%" % (((count * 1.0) / num) * 100)
                count +=1 
                if percent > percent_printed:
                    percent_printed = percent
                    print "Done %s%%" % (percent)
            except except (KeyboardInterrupt, SystemExit):
                print "stopped at %s" % count
            except:
                print "failed for pk %s"  % x.pk
