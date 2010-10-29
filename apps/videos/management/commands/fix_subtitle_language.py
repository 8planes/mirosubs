from django.core.management.base import BaseCommand
from videos.models import Video, SubtitleLanguage

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        qs = SubtitleLanguage.objects.filter(is_complete=True)
        for item in qs:
            if not item.video.version(language_code=item.language):
                item.is_complete = False
                item.was_complete = False
                item.save()