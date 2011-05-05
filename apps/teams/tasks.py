from celery.decorators import task
from utils import send_templated_email
from django.contrib.sites.models import Site
from django.conf import settings

@task()
def add_video_notification(team_video_id):
    """
    Celery task for sending emails to members about new video in team.
    NOTE: It not used now(see command fill_team_video_language), but can be useful in future.
    """
    from teams.models import TeamVideo, Team
    
    domain = Site.objects.get_current().domain
    
    try:
        tv = TeamVideo.objects.get(pk=team_video_id)
    except TeamVideo.DoesNotExist:
        return

    qs = tv.team.users.exclude(pk=tv.added_by).filter(changes_notification=True, is_active=True) \
        .filter(teammember__changes_notification=True)
    
    subject = u'New %s videos ready for subtitling!' % tv.team
    
    for user in qs:
        if not user.email:
            continue
        
        context = {
            'domain': domain,
            'user': user,
            'team': tv.team,
            'team_video': tv
        }
        send_templated_email(user.email, subject, 
                             'teams/email_new_video.html',
                             context, fail_silently=not settings.DEBUG)    
            
@task()
def update_team_video(video_id):
    from teams.models import TeamVideo
    from videos.models import Video
    
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        #if language does not exist - ignore updating
        return

    if isinstance(video, TeamVideo):
        video.update_team_video_language_pairs()
    else:
        for tv in video.teamvideo_set.all():
            tv.update_team_video_language_pairs()

@task()            
def update_team_video_for_sl(sl_id):
    from videos.models import SubtitleLanguage
    from teams.models import TeamVideoLanguage
    
    try:
        sl = SubtitleLanguage.objects.get(id=sl_id)
    except SubtitleLanguage.DoesNotExist:
        #if language does not exist - ignore updating
        return
        
    for tv in sl.video.teamvideo_set.all():
        tv.update_team_video_language_pairs_for_sl(sl)
        TeamVideoLanguage.update_for_language(tv, sl.language)
        
@task()
def update_one_team_video(team_video_id):
    from teams.models import TeamVideo, TeamVideoLanguage
    try:
        team_video = TeamVideo.objects.get(id=team_video_id)
    except TeamVideo.DoesNotExist:
        return
    
    team_video.update_team_video_language_pairs()
    TeamVideoLanguage.update(team_video)