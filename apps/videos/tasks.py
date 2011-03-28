from celery.decorators import task

@task()
def add(x, y):
    print 'TASK IS EXECUTED WITH ARGUMENTS %s AND %s' % (x, y)
    return x + y

@task()
def check_alarm(version_id):
    from videos.models import SubtitleVersion
    from videos import alarms
    
    try:
        version = SubtitleVersion.objects.get(id=version_id)
    except SubtitleVersion.DoesNotExist:
        return

    alarms.check_subtitle_version(version)
    alarms.check_other_languages_changes(version)
    alarms.check_language_name(version)    
    
    
