from celery.decorators import task

@task()
def update_team_video(video):
    from teams.models import TeamVideo

    if isinstance(video, TeamVideo):
        video.update_team_video_language_pairs()
    else:
        for tv in video.teamvideo_set.all():
            tv.update_team_video_language_pairs()

@task()            
def update_team_video_for_sl(sl):
    for tv in sl.video.teamvideo_set.all():
        tv.update_team_video_language_pairs_for_sl(sl)    