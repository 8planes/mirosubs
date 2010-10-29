from django.core.management.base import BaseCommand
from videos.models import SubtitleVersion, StopNotification, SubtitleLanguage
from django.conf import settings
from datetime import datetime, timedelta
from videos.utils import send_templated_email
from django.contrib.sites.models import Site
from django.db.models import Q
import urllib
from django.utils import simplejson as json
from django.utils.http import urlquote_plus

class Command(BaseCommand):
    domain = Site.objects.get_current().domain
    
    def handle(self, *args, **kwargs):
        max_save_time = datetime.now() - timedelta(seconds=settings.EDIT_END_THRESHOLD)
        
        qs = SubtitleVersion.objects \
            .filter(notification_sent=False) \
            .filter(Q(language__writelock_time__isnull=True)|Q(language__writelock_time__lte=max_save_time))
        for version in qs:
            self._update_language(version)
            version.notification_sent = True
            version.save()
            #version.update_changes()  #item is saved in update_changes            
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
        for user in language.notification_list(translation_version.user):
            context = {
                'version': translation_version,
                'domain': self.domain,
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
            
    def send_letter_caption(self, caption_version):
        language = caption_version.language
        qs = SubtitleVersion.objects.filter(language=language) \
            .filter(version_no__lt=caption_version.version_no).order_by('-version_no')
        context = {
            'version': caption_version,
            'domain': self.domain,
            'translation': not language.is_original,
            'video': caption_version.video,
            'language': language
        }
        not_send = StopNotification.objects.filter(video=language.video) \
            .values_list('user_id', flat=True)         
        users = []
        for item in qs:
            if item.user and item.user.is_active and not caption_version.user == item.user and item.user.changes_notification \
                and not item.user in users and not item.user.id in not_send:
                users.append(item.user)
                context['user'] = item.user
                context['old_version'] = item
                
                second_captions = dict([(c.subtitle_id, c) for c in item.subtitles()])
                captions = []
                for caption in caption_version.subtitles():
                    try:
                        scaption = second_captions[caption.subtitle_id]
                    except KeyError:
                        scaption = None
                        changed = True
                    else:
                        changed = not caption.text == scaption.text
                    data = [caption, scaption, changed]
                    captions.append(data)
                context['captions'] = captions
                context['hash'] = item.user.hash_for_video(context['video'].video_id)
                subject = 'New edits to "%s" by %s on Universal Subtitles' % \
                    (language.video.__unicode__(), item.user.__unicode__())
                send_templated_email(item.user.email, subject, 
                                     'videos/email_notification.html',
                                     context, 'feedback@universalsubtitles.org',
                                     fail_silently=not settings.DEBUG)
