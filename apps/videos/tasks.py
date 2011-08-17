from utils.celery_utils import task
from django.utils import simplejson as json
from django.utils.http import urlquote_plus
import urllib
from utils import send_templated_email
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import ObjectDoesNotExist
from celery.signals import task_failure, worker_ready
from haystack import site
from videos.models import VideoFeed, SubtitleLanguage, Video
from sentry.client.models import client
from celery.decorators import periodic_task
from celery.schedules import crontab
from videos.types.youtube import save_subtitles_for_lang
from django.core.files.base import ContentFile
from urllib import urlopen
import logging
from sentry.client.handlers import SentryHandler 

celery_logger = logging.getLogger('celery.task') 
celery_logger.addHandler(SentryHandler())  
def process_failure_signal(exception, traceback, sender, task_id,  
                           signal, args, kwargs, einfo, **kw):  
    exc_info = (type(exception), exception, traceback)  
    celery_logger.error(  
        'Celery job exception: %s(%s)' % (exception.__class__.__name__, exception),  
        exc_info=exc_info,  
        extra={  
            'data': {  
                'task_id': task_id,  
                'sender': sender,  
                'args': args,  
                'kwargs': kwargs,  
            }  
        }  
    )  
task_failure.connect(process_failure_signal)  

@periodic_task(run_every=crontab(hour=3, day_of_week=1))
def cleanup():
    import datetime
    from django.db import transaction
    from django.contrib.sessions.models import Session
    from djcelery.models import TaskState
    
    now = datetime.datetime.now()
    Session.objects.filter(expire_date__lt=now).delete()
    
    d = now - datetime.timedelta(days=31)
    TaskState.objects.filter(tstamp__lt=d).delete()
    transaction.commit_unless_managed()
    
@task
def save_thumbnail_in_s3(video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return

    if video.thumbnail:
        content = ContentFile(urlopen(video.thumbnail).read())
        video.s3_thumbnail.save(video.thumbnail.split('/')[-1], content)
        
@periodic_task(run_every=crontab(minute=0, hour=1))
def update_from_feed(*args, **kwargs):
    for feed in VideoFeed.objects.all():
        update_video_feed.delay(feed.pk)    

@task
def update_subtitles_fetched_counter_for_sl(sl_pk):
    try:
        sl = SubtitleLanguage.objects.get(pk=sl_pk)
        sl.subtitles_fetched_counter.incr()
    except (SubtitleLanguage.DoesNotExist, ValueError):
        return

@task
def update_video_feed(video_feed_id):
    try:
        video_feed = VideoFeed.objects.get(pk=video_feed_id)
        video_feed.update()
    except VideoFeed:
        msg = '**update_video_feed**. VideoFeed does not exist. ID: %s' % video_feed_id
        client.create_from_text(msg, logger='celery')

@task(ignore_result=False)
def add(a, b):
    print "TEST TASK FOR CELERY. EXECUTED WITH ARGUMENTS: %s %s" % (a, b)
    return (a, b, a+b)

@task
def test_task(n):
    if not n:
        print '.'
    
    from time import sleep
    
    for i in xrange(n):
        print '.',
        sleep(0.5)

@task
def raise_exception(msg, **kwargs):
    print "TEST TASK FOR CELERY. RAISE EXCEPTION WITH MESSAGE: %s" % msg
    logger = raise_exception.get_logger()
    logger.error('Test error logging to Sentry from Celery')

    raise TypeError(msg)

@task()
def video_changed_tasks(video_pk, new_version_id=None):
    from videos import metadata_manager
    from videos.models import Video
    from teams.models import TeamVideo
    
    metadata_manager.update_metadata(video_pk)
    if new_version_id is not None:
        _send_notification(new_version_id)
        _check_alarm(new_version_id)
        _detect_language(new_version_id)

    video = Video.objects.get(pk=video_pk)
    if video.teamvideo_set.count() > 0:
        tv_search_index = site.get_index(TeamVideo)
        tv_search_index.backend.update(
            tv_search_index,
            list(video.teamvideo_set.all()))
    
    video.update_search_index()
    
@task()
def send_change_title_email(video_id, user_id, old_title, new_title):
    from videos.models import Video
    from auth.models import CustomUser as User
    
    domain = Site.objects.get_current().domain
    
    try:
        video = Video.objects.get(id=video_id)
        user = user_id and User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return
    
    users = video.notification_list(user)
    
    for obj in users:
        subject = u'Video\'s title changed on Universal Subtitles'
        context = {
            'user': obj,
            'domain': domain,
            'video': video,
            'editor': user,
            'old_title': old_title,
            'hash': obj.hash_for_video(video.video_id),
            'new_title': new_title
        }
        send_templated_email(obj.email, subject, 
                             'videos/email_title_changed.html',
                             context, fail_silently=not settings.DEBUG)       
    
def _send_notification(version_id):
    from videos.models import SubtitleVersion
    
    try:
        version = SubtitleVersion.objects.get(id=version_id)
    except SubtitleVersion.DoesNotExist:
        return

    if version.result_of_rollback:
        return

    version.notification_sent = True
    version.save()
    if version.version_no == 0 and not version.language.is_original:
        _send_letter_translation_start(version)
    else:
        if version.text_change or version.time_change:
            _send_letter_caption(version)        

def _check_alarm(version_id):
    from videos.models import SubtitleVersion
    from videos import alarms
    
    try:
        version = SubtitleVersion.objects.get(id=version_id)
    except SubtitleVersion.DoesNotExist:
        return

    alarms.check_subtitle_version(version)
    alarms.check_other_languages_changes(version)
    alarms.check_language_name(version)    

def _detect_language(version_id):
    from videos.models import SubtitleVersion, SubtitleLanguage
    
    try:
        version = SubtitleVersion.objects.get(id=version_id)
    except SubtitleVersion.DoesNotExist:
        return    

    language = version.language
    if language.is_original and not language.language:
        url = 'http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q=%s'
        text = ''
        for item in version.subtitles():
            text += ' %s' % item.text
            if len(text) >= 300:
                break
        r = json.loads(urllib.urlopen(url % urlquote_plus(text)).read())

        if r and not 'error' in r:
            try:
                SubtitleLanguage.objects.get(video=language.video, language=r['responseData']['language'])
            except SubtitleLanguage.DoesNotExist:
                language.language = r['responseData']['language']
                language.save()  

def _send_letter_translation_start(translation_version):
    domain = Site.objects.get_current().domain
    video = translation_version.language.video
    language = translation_version.language
    for user in video.notification_list(translation_version.user):
        context = {
            'version': translation_version,
            'domain': domain,
            'video_url': 'http://%s%s' % (domain, video.get_absolute_url()),
            'user': user,
            'language': language,
            'video': video,
            'hash': user.hash_for_video(video.video_id)
        }
        subject = 'New %s translation by %s of "%s"' % \
            (language.language_display(), translation_version.user.__unicode__(), video.__unicode__())
        send_templated_email(user.email, subject, 
                             'videos/email_start_notification.html',
                             context, fail_silently=not settings.DEBUG)

def _make_caption_data(new_version, old_version):
    second_captions = dict([(item.subtitle_id, item) for item in old_version.ordered_subtitles()])
    first_captions = dict([(item.subtitle_id, item) for item in new_version.ordered_subtitles()])

    subtitles = {}

    for id, item in first_captions.items():
        if not id in subtitles:
            subtitles[id] = item.start_time

    for id, item in second_captions.items():
        if not id in subtitles:
            subtitles[id] = item.start_time

    subtitles = [item for item in subtitles.items()]
    subtitles.sort(key=lambda item: item[1])

    captions = []
    for subtitle_id, t in subtitles:
        try:
            scaption = second_captions[subtitle_id]
        except KeyError:
            scaption = None
        try:
            fcaption = first_captions[subtitle_id]
        except KeyError:
            fcaption = None

        if fcaption is None or scaption is None:
            changed = dict(text=True, time=True)
        else:
            changed = {
                'text': (not fcaption.text == scaption.text),
                'time': (not fcaption.start_time == scaption.start_time),
                'end_time': (not fcaption.end_time == scaption.end_time)
            }
        data = [fcaption, scaption, changed]
        captions.append(data)
    return captions

def _send_letter_caption(caption_version):
    from videos.models import SubtitleVersion

    domain = Site.objects.get_current().domain
    
    language = caption_version.language
    video = language.video
    qs = SubtitleVersion.objects.filter(language=language) \
        .filter(version_no__lt=caption_version.version_no).order_by('-version_no')
    if qs.count() == 0:
        return

    most_recent_version = qs[0]
    captions = _make_caption_data(caption_version, most_recent_version)
    context = {
        'version': caption_version,
        'domain': domain,
        'translation': not language.is_original,
        'video': caption_version.video,
        'language': language,
        'last_version': most_recent_version,
        'captions': captions,
        'video_url': video.get_absolute_url(),
        'language_url': language.get_absolute_url(),
        'user_url': caption_version.user and caption_version.user.get_absolute_url()
    }

    subject = u'New edits to "%s" by %s on Universal Subtitles' % (language.video, caption_version.user)

    users = []

    followers = set(video.notification_list(caption_version.user))
    followers.update(language.notification_list(caption_version.user))
    
    for item in qs:
        if item.user and item.user in followers:
            context['your_version'] = item
            context['user'] = item.user
            context['hash'] = item.user.hash_for_video(context['video'].video_id)
            send_templated_email(item.user.email, subject, 
                                 'videos/email_notification.html',
                                 context, fail_silently=not settings.DEBUG)

            followers.discard(item.user)
    
    for user in followers:
        context['user'] = user
        context['hash'] = user.hash_for_video(context['video'].video_id)
        send_templated_email(user.email, subject, 
                             'videos/email_notification_non_editors.html',
                             context, fail_silently=not settings.DEBUG)        
