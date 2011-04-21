from django.core.management.base import BaseCommand
from videos.models import SubtitleLanguage
from time import sleep

WAIT_BETWEEN_WRITES = 1

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print 'Run recalculate all sub langs count & percent done'
        all_count = SubtitleLanguage.objects.all().count() * 1.0
        updated = 0
        percent_done = 0
        for sl in SubtitleLanguage.objects.all():
            sl.update_percent_done()
            sl.update_complete_state()
            sleep(WAIT_BETWEEN_WRITES)
            updated += 1
            new_percent_done = int((updated / all_count) * 100)
            if new_percent_done != percent_done:
                print "%s%% done" % percent_done
                percent_done = new_percent_done
            
