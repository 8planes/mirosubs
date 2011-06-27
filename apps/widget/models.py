from django.db import models
from auth.models import CustomUser as User
from videos.models import SubtitleLanguage, SubtitleVersion

class SubtitlingSession(models.Model):
    language = models.ForeignKey(
        SubtitleLanguage, related_name='subtitling_sessions')
    base_language = models.ForeignKey(
        SubtitleLanguage, null=True, related_name='based_subtitling_sessions')
    parent_version = models.ForeignKey(SubtitleVersion, null=True)
    user = models.ForeignKey(User, null=True)
    browser_id = models.CharField(max_length=128, blank=True)
    datetime_started = models.DateTimeField(auto_now_add=True)

    @property
    def video(self):
        return self.language.video

    def matches_request(self, request):
        if request.user.is_authenticated() and self.user:
            return self.user == request.user
        else:
            return request.browser_id == self.browser_id

