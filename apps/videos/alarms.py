from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models import Q, Count
from statistic.models import SubtitleFetchCounters
from datetime import date, datetime, timedelta
from videos.models import SubtitleLanguage
import urllib2
from django.utils import simplejson
from django.utils.http import urlquote_plus

ALARM_EMAIL = settings.ALARM_EMAIL

if not isinstance(ALARM_EMAIL, (list, tuple)):
    ALARM_EMAIL = [ALARM_EMAIL]

def send_alarm_email(version, type):
        subject = u'Alert: %s [%s]' % (version.language.video, type)
        url = version.language.get_absolute_url()
        message = u'Language: http://%s%s' % (Site.objects.get_current().domain, url)
        if version.user:
            message += 'User: %s' %  version.user
        send_mail(subject, message, from_email=settings.SERVER_EMAIL, recipient_list=ALARM_EMAIL, 
                  fail_silently=True)    

def check_subtitle_version(version):
    if not ALARM_EMAIL:
        return
    
    prev_version = version.prev_version()

    if not prev_version:
        return
    
    ###########################
    cur_ver_len = version.subtitle_set.count()
    prev_ver_len = prev_version.subtitle_set.count()

    if prev_ver_len == 0:
        return 
     
    if (float(cur_ver_len) / prev_ver_len) <= 0.7:
        send_alarm_email(version, u'A translation loses more than 30% of its lines')
    
    ############################
    cur_ver_len = version.subtitle_set.filter(Q(start_time__isnull=False), \
                                               Q(end_time__isnull=False)).count()
    prev_ver_len = prev_version.subtitle_set.filter(Q(start_time__isnull=False), \
                                               Q(end_time__isnull=False)).count()    
    
    if prev_ver_len == 0:
        return
    
    if (float(cur_ver_len) / prev_ver_len) <= 0.7:
        send_alarm_email(version, u'A translation loses more than 30% of its syncing information')

def check_other_languages_changes(version, ignore_statistic=False):
    if not ALARM_EMAIL:
        return
    
    if not ignore_statistic:
        fetch_count = SubtitleFetchCounters.objects.filter(video=version.language.video, date=date.today()) \
            .aggregate(fetch_count=Count('count'))['fetch_count']
        
        if fetch_count < 100:
            return
    
    d = datetime.now() - timedelta(hours=1)
    
    changed_langs_count = SubtitleLanguage.objects.filter(video=version.language.video) \
        .filter(subtitleversion__datetime_started__gte=d).count()
        
    all_langs_count = SubtitleLanguage.objects.filter(video=version.language.video).count()
    
    if (float(changed_langs_count) / all_langs_count) >= 0.5:
        send_alarm_email(version, u'A video had changes made two more than 50% of its languages in the last hour')

def check_language_name(version, ignore_statistic=False):
    if not ignore_statistic:
        fetch_count = SubtitleFetchCounters.objects.filter(video=version.language.video, date=date.today()) \
            .aggregate(fetch_count=Count('count'))['fetch_count']
        
        if fetch_count < 100:
            return
    
    text = ''
    
    for s in version.subtitles():
        text += (' '+s.text)
        
        if len(text) >= 400:
            break
    
    url = u'https://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q=%s'
    url = url % urlquote_plus(text)

    request = urllib2.Request(url, None)
    response = urllib2.urlopen(request)
    
    results = simplejson.load(response)

    lang = version.language
    
    if results['responseStatus'] == 200:
        if not results['responseData']['isReliable'] or \
                (lang.language and lang.language != results['responseData']['language']):
            send_alarm_email(version, u'Text does not look like language labeled')    
        

        