from utils.celery_search_index import LogEntry
from utils.celery_utils import task
from celery.schedules import crontab
from celery.decorators import periodic_task
from django.core.management import call_command

@periodic_task(run_every=crontab(minute=0, hour=0))
def update_search_index():
    call_command('update_index', verbosity=2)