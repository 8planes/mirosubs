import sys
from django.core.management.base import BaseCommand
from videos.models import Video, VideoUrl, Action, SubtitleLanguage
from django.core.exceptions import ObjectDoesNotExist
from utils import SrtSubtitleParser
import httplib2
import chardet
from videos.forms import SubtitlesUploadForm
from videos.types.youtube import YoutubeVideoType
from videos.types import video_type_registrar
from django.utils.encoding import force_unicode
from django.core.files.uploadedfile import SimpleUploadedFile
from auth.models import CustomUser
import feedparser
import re

VIDEOID_RE = re.compile(r'([A-Za-z_\-0-9]+)\w*$')

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        startIndex = 0
        if len(args) > 0:
            startIndex = int(args[0])
        feed = feedparser.parse(
            "http://ocw.mit.edu/rss/new/ocw_youtube_videos.xml")
        i = 1
        count = len(feed.entries)
        for item in feed.entries:
            if hasattr(item, 'videodownload'):
                if i < startIndex:
                    i += 1
                    continue
                print('importing {0}, {1}/{2}'.format(
                        item.videoid, i, count))
                i += 1
                videosrt = None
                if hasattr(item, 'videosrt'):
                    videosrt = item.videosrt
                try:
                    self._import_video(
                        item.videodownload,
                        item.videoid,
                        item.title,
                        item.description,
                        item.thumbnail,
                        videosrt)
                except:
                    print sys.exc_info()

    def _import_video(self, video_url, videoid, title, description, thumbnail, videosrt):
        videoid_match = VIDEOID_RE.search(videoid)
        videoid = videoid_match.group(1)
        video_type = YoutubeVideoType(
            'http://www.youtube.com/watch?v={0}'.format(videoid))
        try:
            video_url_obj = VideoUrl.objects.get(
                url=video_type.convert_to_video_url())
            video = video_url_obj.video
        except ObjectDoesNotExist:
            video_url_obj = None
            video = Video()
            video.youtube_videoid = videoid
        video.title = title
        video.description = description
        if video_type.entry.media.duration:
            video.duration = int(video_type.entry.media.duration.seconds)
        video.thumbnail = thumbnail
        video.save()
        Action.create_video_handler(video)

        if videosrt:
            self._import_srt(video, videosrt)
        else:
            SubtitleLanguage(video=video, language='en', is_original=True, is_forked=True).save()

        if not video_url_obj:
            video_url_obj = VideoUrl(
                videoid=videoid,
                url=video_type.convert_to_video_url(),
                type=video_type.abbreviation,
                original=True,
                primary=True,
                video=video)
            video_url_obj.save()

        self._save_alternate_url(video, video_url)

    def _import_srt(self, video, videosrt_url):
        h = httplib2.Http()
        resp, content = h.request(videosrt_url, "GET")

        if resp.status == 200:
            data = {'video': video.id,
                    'language': 'en',
                    'video_language': 'en',
                    'is_complete': True }
            file_data = {'subtitles': SimpleUploadedFile('subs.srt', content)}
            form = SubtitlesUploadForm(
                CustomUser.get_anonymous(), data, file_data)
            if form.is_valid():
                form.save()
            else:
                print('url {0} did not return valid srt data'.format(videosrt_url))

    def _save_alternate_url(self, video, video_url):
        video_type = video_type_registrar.video_type_for_url(video_url)
        video_url_obj, created = VideoUrl.objects.get_or_create(
            url=video_type.convert_to_video_url(),
            defaults=dict(
                type=video_type.abbreviation,
                original=True,
                primary=False,
                video=video))
