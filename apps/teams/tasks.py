from celery.decorators import task

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