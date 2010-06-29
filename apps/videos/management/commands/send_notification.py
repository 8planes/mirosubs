from django.core.management.base import BaseCommand
from videos.models import VideoCaptionVersion, TranslationVersion
from django.conf import settings
from datetime import datetime, timedelta
from videos.utils import send_templated_email
from django.contrib.sites.models import Site

class Command(BaseCommand):
    domain = Site.objects.get_current().domain
    
    def handle(self, *args, **kwargs):
        max_save_time = datetime.now() - timedelta(seconds=settings.EDIT_END_THRESHOLD)
        
        qs = VideoCaptionVersion.objects \
            .filter(notification_sent=False) \
            .filter(datetime_started__lte=max_save_time)
        for version in qs:
            version.notification_sent = True
            version.update_changes()  #item is saved in update_changes
            self.send_letter_caption(version)
        
        translation_qs = TranslationVersion.objects \
            .filter(notification_sent=False) \
            .filter(datetime_started__lte=max_save_time)
        for version in translation_qs:
            version.notification_sent = True
            version.update_changes()  #item is saved in update_changes            
            if version.version_no == 0:
                self.send_letter_translation_start(version)
            else:
                self.send_letter_translation(version)
    
    def send_letter_translation_start(self, translation_version):
        video = translation_version.language.video
        if video.owner and not video.owner == translation_version.user and video.owner.changes_notification:
            context = {
                'version': translation_version,
                'domain': self.domain,
                'user': video.owner,
                'language': translation_version.language,
                'video': video
            }
            send_templated_email(video.owner.email, '', 'videos/email_start_notification.html',
                         context, fail_silently=not settings.DEBUG)
            
    def send_letter_translation(self, translation_version):
        qs = TranslationVersion.objects.filter(language=translation_version.language) \
            .filter(version_no__lt=translation_version.version_no).order_by('-version_no')
        context = {
            'version': translation_version,
            'domain': self.domain,
            'translation': True
        }
        users = []
        for item in qs:
            if not translation_version.user == item.user and item.user.changes_notification \
                                                    and not item.user in users:
                users.append(item.user)
                context['user'] = item.user
                context['old_version'] = item
                send_templated_email(item.user.email, '', 'videos/email_notification.html',
                             context, fail_silently=not settings.DEBUG)            
            
    def send_letter_caption(self, caption_version):
        qs = VideoCaptionVersion.objects.filter(video=caption_version.video) \
            .filter(version_no__lt=caption_version.version_no).order_by('-version_no')
        context = {
            'version': caption_version,
            'domain': self.domain,
            'translation': False
        }
        users = []
        for item in qs:
            if not caption_version.user == item.user and item.user.changes_notification \
                                                    and not item.user in users:
                users.append(item.user)
                context['user'] = item.user
                context['old_version'] = item
                send_templated_email(item.user.email, '', 'videos/email_notification.html',
                             context, fail_silently=not settings.DEBUG)