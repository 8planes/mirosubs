from utils.celery_utils import task
from utils import send_templated_email
from django.contrib.sites.models import Site
from django.conf import settings
from celery.decorators import periodic_task
from celery.schedules import crontab
from datetime import datetime, timedelta
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from haystack import site

#@periodic_task(run_every=crontab(minute=0, hour=6))
@periodic_task(run_every=timedelta(seconds=60))
def add_videos_notification(*args, **kwargs):
    from teams.models import TeamVideo, Team
    
    domain = Site.objects.get_current().domain
    
    qs = Team.objects.filter(teamvideo__created__gt=F('last_notification_time')).distinct()
    
    for team in qs:
        team_videos = TeamVideo.objects.filter(team=team, created__gt=team.last_notification_time)

        team.last_notification_time = datetime.now()
        team.save()

        members = team.users.filter(changes_notification=True, is_active=True) \
            .filter(teammember__changes_notification=True).distinct()

        subject = _(u'New %(team)s videos ready for subtitling!') % dict(team=team)

        for user in members:
            if not user.email:
                continue

            context = {
                'domain': domain,
                'user': user,
                'team': team,
                'team_videos': team_videos
            }

            send_templated_email(user.email, subject, 
                                 'teams/email_new_videos.html',
                                 context, fail_silently=not settings.DEBUG)


@task()
def update_one_team_video(team_video_id):
    from teams.models import TeamVideo, TeamVideoLanguage
    try:
        team_video = TeamVideo.objects.get(id=team_video_id)
    except TeamVideo.DoesNotExist:
        return

    tv_search_index = site.get_index(TeamVideo)
    tv_search_index.backend.update(
        tv_search_index, [team_video])
