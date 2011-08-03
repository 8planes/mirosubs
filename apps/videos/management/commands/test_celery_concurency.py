from django.core.management.base import BaseCommand
import random
from time import sleep

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        from videos.tasks import test_task
        while True:
            if random.random() < 0.75:
                test_task.delay(0)
                print 0
            else:
                i = int(random.random()*20)
                test_task.delay(i)
                print i
            
            sleep(0.2)