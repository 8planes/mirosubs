from django.core.management.base import BaseCommand
from videos.models import SubtitleVersion, SubtitleLanguage
from django.conf import settings
from datetime import datetime, timedelta
from utils import send_templated_email
from django.contrib.sites.models import Site
from django.db.models import Q
import urllib
from django.utils import simplejson as json
from django.utils.http import urlquote_plus
from django.core.urlresolvers import reverse

class Command(BaseCommand):
    domain = Site.objects.get_current().domain
    
    def handle(self, *args, **kwargs):
        print 'Run send_notification command'
        max_save_time = datetime.now() - timedelta(seconds=settings.EDIT_END_THRESHOLD)
        
        qs = SubtitleVersion.objects \
            .filter(notification_sent=False) \
            .filter(Q(language__writelock_time__isnull=True)|Q(language__writelock_time__lte=max_save_time))
        for version in qs:
            self._update_language(version)
            version.notification_sent = True
            version.save()
            if version.version_no == 0 and not version.language.is_original:
                self.send_letter_translation_start(version)
            else:
                if version.text_change or version.time_change:
                    self.send_letter_caption(version)
    
    def _update_language(self, version):
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

    def send_letter_translation_start(self, translation_version):
        video = translation_version.language.video
        language = translation_version.language
        for user in video.notification_list(translation_version.user):
            context = {
                'version': translation_version,
                'domain': self.domain,
                'video_url': 'http://{0}{1}'.format(
                    self.domain, reverse('videos:video', [video.id])),
                'user': user,
                'language': language,
                'video': video,
                'hash': user.hash_for_video(video.video_id)
            }
            subject = 'New %s translation by %s of "%s"' % \
                (language.language_display(), translation_version.user.__unicode__(), video.__unicode__())
            send_templated_email(user.email, subject, 
                                 'videos/email_start_notification.html',
                                 context, 'feedback@universalsubtitles.org', 
                                 fail_silently=not settings.DEBUG)

    def _make_caption_data(self, new_version, old_version):
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

    def send_letter_caption(self, caption_version):
        language = caption_version.language
        video = language.video
        qs = SubtitleVersion.objects.filter(language=language) \
            .filter(version_no__lt=caption_version.version_no).order_by('-version_no')
        if qs.count() == 0:
            return
        most_recent_version = qs[0]
        captions = self._make_caption_data(caption_version, most_recent_version)
        context = {
            'version': caption_version,
            'domain': self.domain,
            'translation': not language.is_original,
            'video': caption_version.video,
            'language': language,
            'last_version': most_recent_version,
            'captions': captions,
            'video_url': language.get_absolute_url()
        }
        subject = 'New edits to "%s" by %s on Universal Subtitles' % \
            (language.video.__unicode__(), caption_version.user.__unicode__())
 
        users = []
        
        video_followers = video.notification_list([caption_version.user])
        
        for item in qs:
            users.append(item.user)
            if item.user and not item.user in users and item.user in video_followers:
                context['your_version'] = item
                context['user'] = item.user
                context['hash'] = item.user.hash_for_video(context['video'].video_id)
                send_templated_email(item.user.email, subject, 
                                     'videos/email_notification.html',
                                     context, 'feedback@universalsubtitles.org',
                                     fail_silently=not settings.DEBUG)
