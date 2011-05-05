from celery.decorators import task
from django.utils import simplejson as json
from django.utils.http import urlquote_plus
import urllib
from utils import send_templated_email
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import ObjectDoesNotExist

@task()
def add(x, y):
    print 'TASK IS EXECUTED WITH ARGUMENTS %s AND %s' % (x, y)
    return x + y

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
    
@task()
def send_notification(version_id):
    from videos.models import SubtitleVersion
    
    try:
        version = SubtitleVersion.objects.get(id=version_id)
    except SubtitleVersion.DoesNotExist:
        return
    
    version.notification_sent = True
    version.save()
    if version.version_no == 0 and not version.language.is_original:
        _send_letter_translation_start(version)
    else:
        if version.text_change or version.time_change:
            _send_letter_caption(version)        

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

@task()
def detect_language(version_id):
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

        if not 'error' in r:
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
        'video_url': language.get_absolute_url(),
        'user_url': caption_version.user and caption_version.user.get_absolute_url()
    }

    subject = u'New edits to "%s" by %s on Universal Subtitles' % (language.video, caption_version.user)

    users = []

    video_followers = video.notification_list(caption_version.user)
    language_followers = language.notification_list(caption_version.user)

    for item in qs:
        if item.user and not item.user in users and (item.user in video_followers or \
            item.user in language_followers):
            context['your_version'] = item
            context['user'] = item.user
            context['hash'] = item.user.hash_for_video(context['video'].video_id)
            send_templated_email(item.user.email, subject, 
                                 'videos/email_notification.html',
                                 context, fail_silently=not settings.DEBUG)

        users.append(item.user)              