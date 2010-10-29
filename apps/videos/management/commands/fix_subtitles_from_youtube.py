from django.core.management.base import BaseCommand
from videos.models import Video, VIDEO_TYPE_YOUTUBE, SubtitleVersion
from datetime import datetime, timedelta
from auth.models import CustomUser as User

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        two_days_ago = datetime.today() - timedelta(days=2)
        user = User.get_youtube_anonymous()
        
        qs = SubtitleVersion.objects.filter(datetime_started__gte=two_days_ago) \
            .filter(language__video__video_type=VIDEO_TYPE_YOUTUBE) \
            .filter(user=user)
        
        for version in qs:
            language = version.language
            SubtitleVersion.objects.filter(language=language).delete()
            language.video._get_subtitles_from_youtube(language=language)
            