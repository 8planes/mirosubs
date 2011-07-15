from celery.decorators import periodic_task
from statistic import st_sub_fetch_handler, st_video_view_handler, st_widget_view_statistic
from datetime import timedelta
from utils.celery_utils import task

@periodic_task(run_every=timedelta(hours=6))
#@periodic_task(run_every=timedelta(seconds=30))
def update_statistic(*args, **kwargs):
    count = st_sub_fetch_handler.migrate(verbosity=kwargs.get('verbosity', 1))
    count = st_video_view_handler.migrate(verbosity=kwargs.get('verbosity', 1))
    count = st_widget_view_statistic.migrate(verbosity=kwargs.get('verbosity', 1))

@task
def st_sub_fetch_handler_update(*args, **kwargs):
    st_sub_fetch_handler.update(*args, **kwargs)

@task
def st_video_view_handler_update(*args, **kwargs):
    st_video_view_handler.update(*args, **kwargs)

@task
def st_widget_view_statistic_update(*args, **kwargs):
    st_widget_view_statistic.update(*args, **kwargs)