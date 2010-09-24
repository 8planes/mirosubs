# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.db import models
import string
import random
import re
from urlparse import urlparse, parse_qs
from django.conf.global_settings import LANGUAGES
from auth.models import CustomUser as User, Awards
from datetime import datetime, date, timedelta
from django.db.models.signals import post_save
from django.utils.dateformat import format as date_format
from gdata.youtube.service import YouTubeService
from comments.models import Comment
from vidscraper.sites import blip, google_video, fora, ustream, vimeo
from youtube import get_video_id
import dailymotion
import urllib
from videos.utils import YoutubeSubtitleParser
from django.db.models.signals import post_save
from videos import EffectiveSubtitle

yt_service = YouTubeService()
yt_service.ssl = False

NO_SUBTITLES, SUBTITLES_FINISHED = range(2)
VIDEO_TYPE_HTML5 = 'H'
VIDEO_TYPE_YOUTUBE = 'Y'
VIDEO_TYPE_BLIPTV = 'B'
VIDEO_TYPE_GOOGLE = 'G'
VIDEO_TYPE_FORA = 'F'
VIDEO_TYPE_USTREAM = 'U'
VIDEO_TYPE_VIMEO = 'V'
VIDEO_TYPE_DAILYMOTION = 'D'
VIDEO_TYPE_FLV = 'L'
VIDEO_TYPE = (
    (VIDEO_TYPE_HTML5, 'HTML5'),
    (VIDEO_TYPE_YOUTUBE, 'Youtube'),
    (VIDEO_TYPE_BLIPTV, 'Blip.tv'),
    (VIDEO_TYPE_GOOGLE, 'video.google.com'),
    (VIDEO_TYPE_FORA, 'Fora.tv'),
    (VIDEO_TYPE_USTREAM, 'Ustream.tv'),
    (VIDEO_TYPE_VIMEO, 'Vimeo.com'),
    (VIDEO_TYPE_DAILYMOTION, 'dailymotion.com'),
    (VIDEO_TYPE_FLV, 'FLV')
)
WRITELOCK_EXPIRATION = 30 # 30 seconds
VIDEO_SESSION_KEY = 'video_session'
FLV_REGEX = re.compile(r"\.flv$")

class Video(models.Model):
    """Central object in the system"""
    video_id = models.CharField(max_length=255, unique=True)
    video_type = models.CharField(max_length=1, choices=VIDEO_TYPE)
    # only nonzero length for HTML5 videos
    video_url = models.URLField(max_length=2048, blank=True)
    # only nonzero length for Youtube videos
    youtube_videoid = models.CharField(max_length=32, blank=True)
    # only nonzero length for Blip.tv videos
    bliptv_fileid = models.CharField(max_length=32, blank=True)
    bliptv_flv_url = models.CharField(max_length=256, blank=True)
    # only nonzero length for Vimeo videos
    vimeo_videoid = models.CharField(max_length=32, blank=True)
    # only nonzero length for Dailymotion videos
    dailymotion_videoid = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=2048, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(null=True, blank=True)
    allow_community_edits = models.BooleanField()
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255)
    writelock_owner = models.ForeignKey(User, null=True, 
                                        related_name="writelock_owners")
    subtitles_fetched_count = models.IntegerField(default=0)
    widget_views_count = models.IntegerField(default=0)
    is_subtitled = models.BooleanField(default=False)
    was_subtitled = models.BooleanField(default=False)
    thumbnail = models.CharField(max_length=500, blank=True)
    
    def __unicode__(self):
        return self.title_display()
        if self.title:
            return self.title
        if self.video_type == VIDEO_TYPE_HTML5:
            return self.video_url
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            return self.youtube_videoid
        elif self.video_type == VIDEO_TYPE_BLIPTV:
            return self.bliptv_fileid
        elif self.video_type == VIDEO_TYPE_VIMEO:
            return self.get_video_url()
        elif self.video_type == VIDEO_TYPE_DAILYMOTION:
            return self.get_video_url()
    
    def is_html5(self):
        return self.video_type == VIDEO_TYPE_HTML5
    
    def title_display(self):
        if self.title:
            return self.title

        url = self.video_url
        url = url.strip('/')

        if url.startswith('http://'):
            url = url[7:]

        parts = url.split('/')
        if len(parts) > 1:
            return '%s/.../%s' % (parts[0], parts[-1])
        else:
            return url

    def search_page_url(self):
        return self.get_absolute_url()

    @models.permalink
    def get_absolute_url(self):
        return ('videos:video', [self.video_id])

    def get_video_url(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return self.video_url
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            return 'http://www.youtube.com/watch?v={0}'.format(self.youtube_videoid)
        elif self.video_type == VIDEO_TYPE_BLIPTV:
            return 'http://blip.tv/file/{0}/'.format(self.bliptv_fileid)
        elif self.video_type == VIDEO_TYPE_VIMEO:
            return 'http://vimeo.com/{0}'.format(self.vimeo_videoid)
        elif self.video_type == VIDEO_TYPE_DAILYMOTION:
            return 'http://dailymotion.com/video/{0}'.format(self.dailymotion_videoid)
        else:
            return self.video_url

    def _get_subtitles_from_youtube(self):
        if not self.youtube_videoid:
            return 

        url = 'http://www.youtube.com/watch_ajax?action_get_caption_track_all&v=%s' % self.youtube_videoid
        d = urllib.urlopen(url)
        parser = YoutubeSubtitleParser(d.read())
        
        if not parser:
            return
        
        language = SubtitleLanguage(video=self)
        language.is_original = False
        language.language = parser.language
        language.save()
        
        version = SubtitleVersion(language=language)
        version.datetime_started = datetime.now()
        version.user = User.get_youtube_anonymous()
        version.note = u'From youtube'
        version.save()
        
        for i, item in enumerate(parser):
            subtitle = Subtitle(**item)
            subtitle.version = version
            subtitle.subtitle_id = int(random.random()*10e12)
            subtitle.sub_order = i+1
            subtitle.save()
        
        version.finished = True
        version.save()
        
        language.is_complete = True
        language.save()

    @classmethod
    def get_or_create_for_url(cls, video_url):
        parsed_url = urlparse(video_url)
        if 'youtube.com' in parsed_url.netloc:
            yt_video_id = get_video_id(video_url)
            video, created = Video.objects.get_or_create(
                youtube_videoid=yt_video_id,
                defaults={'video_type': VIDEO_TYPE_YOUTUBE, 
                          'allow_community_edits': True})
         
            if created:
                entry = yt_service.GetYouTubeVideoEntry(video_id=video.youtube_videoid)
                video.title = entry.media.title.text
                video.duration = entry.media.duration.seconds
                if entry.media.thumbnail:
                    video.thumbnail = entry.media.thumbnail[-1].url
                video.save()
                video._get_subtitles_from_youtube()
        elif 'blip.tv' in parsed_url.netloc and blip.BLIP_REGEX.match(video_url):
            bliptv_fileid = blip.BLIP_REGEX.match(video_url).groupdict()['file_id']
            video, created = Video.objects.get_or_create(
                bliptv_fileid=bliptv_fileid,
                defaults={'video_type': VIDEO_TYPE_HTML5, 
                          'allow_community_edits': True})
            if created:
                video.title = blip.scrape_title(video_url)
                video.bliptv_flv_url = blip.scrape_file_url(video_url)
                video.video_url = video.bliptv_flv_url
                video.thumbnail = blip.get_thumbnail_url(video_url)
                video.save()
        elif 'video.google.com' in parsed_url.netloc and google_video.GOOGLE_VIDEO_REGEX.match(video_url):
            video, created = Video.objects.get_or_create(
                video_url=video_url,
                defaults={'video_type': VIDEO_TYPE_GOOGLE,
                          'allow_community_edits': True})
            if created:
                video.title = google_video.scrape_title(video_url)
                video.save()           
        elif 'ustream.tv' in parsed_url.netloc and ustream.USTREAM_REGEX.match(video_url):
            video, created = Video.objects.get_or_create(
                video_url=ustream.get_flash_enclosure_url(video_url),
                defaults={'video_type': VIDEO_TYPE_USTREAM,
                          'allow_community_edits': True})
            if created:
                video.title = ustream.get_title(video_url)
                video.thumbnail = ustream.get_thumbnail_url(video_url)
                video.save()  
        elif 'vimeo.com' in parsed_url.netloc and vimeo.VIMEO_REGEX.match(video_url):
            vimeo_videoid = vimeo.VIMEO_REGEX.match(video_url).group(2)
            video, created = Video.objects.get_or_create(
                vimeo_videoid = vimeo_videoid,
                defaults={'video_type': VIDEO_TYPE_VIMEO,
                          'allow_community_edits': True})
            # TODO: title and thumbnail -- we can't get them without
            # an application oauth key/secret
        elif 'dailymotion.com' in parsed_url.netloc and dailymotion.DAILYMOTION_REGEX.match(video_url):
            metadata = dailymotion.get_metadata(video_url)

            stream_flv_mini_url = metadata.get('stream_flv_mini_url', '')
            if stream_flv_mini_url and stream_flv_mini_url != '':
                dailymotion_videoid = dailymotion.get_video_id(video_url)
                video, created = Video.objects.get_or_create(
                    dailymotion_videoid = dailymotion_videoid,
                    defaults={'video_type': VIDEO_TYPE_DAILYMOTION,
                              'allow_community_edits': True})
                if created:
                    video.title = metadata.get('title') or dailymotion_videoid
                    video.thumbnail = metadata.get('thumbnail_url') or ''
                    video.save()
            else:
                # not hosted by dailymotion and uses a different player
                # TODO: error message / specific exception type?
                raise Exception("dailymotion video actually hosted by partner -- we can't handle this")
        elif FLV_REGEX.match(video_url):
            video, created = Video.objects.get_or_create(
                video_url=video_url,
                defaults={'video_type': VIDEO_TYPE_FLV,
                          'allow_community_edits': True})
        else:
            video, created = Video.objects.get_or_create(
                video_url=video_url,
                defaults={'video_type': VIDEO_TYPE_HTML5,
                          'allow_community_edits': True})
        return video, created
    
    @property
    def filename(self):
        if self.video_type == VIDEO_TYPE_HTML5:
            return '{0}'.format(self.video_url.split('/')[-1])
        elif self.video_type == VIDEO_TYPE_YOUTUBE:
            return 'youtube_{0}'.format(self.youtube_videoid)
        else:
            return 'bliptv_{0}'.format(self.bliptv_fileid)
            
    def lang_filename(self, lang):
        name = self.filename
        if lang:
            return '%s.%s' % (name[:-4], lang)
        return name
    
    @property
    def subtitle_state(self):
        """Subtitling state for this video 
        """
        return NO_SUBTITLES if self.latest_finished_version() \
            is None else SUBTITLES_FINISHED

    def _original_subtitle_language(self):
        if not hasattr(self, '_original_subtitle'):
            try:
                original = self.subtitlelanguage_set.filter(is_original=True)[:1].get()
            except models.ObjectDoesNotExist:
                original = None

            setattr(self, '_original_subtitle', original)

        return getattr(self, '_original_subtitle')       

    def subtitle_language(self, language_code=None):
        try:
            if language_code is None:
                return self._original_subtitle_language()
            else:
                return self.subtitlelanguage_set.filter(
                    language=language_code)[:1].get()
        except models.ObjectDoesNotExist:
            return None

    def version(self, version_no=None, language_code=None):
        language = self.subtitle_language(language_code)
        return None if language is None else language.version(version_no)

    def latest_finished_version(self, language_code=None):
        language = self.subtitle_language(language_code)
        return None if language is None else language.latest_finished_version()

    def subtitles(self, version_no=None, language_code=None):
        version = self.version(version_no, language_code)
        if version:
            return version.subtitles()
        else:
            return Subtitle.objects.none()

    def latest_finished_subtitles(self, language_code=None):
        version = self.latest_finished_version(language_code)
        return [] if version is None else version.subtitles()

    def null_subtitles(self, user, language_code=None):
        """Returns NullSubtitles for user, or None if none exist."""
        try:
            return self.nullsubtitles_set.filter(
                user__id__exact=user.id).filter(
                language=('' if language_code is None 
                          else language_code))[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def translation_language_codes(self):
        """All iso language codes with finished translations."""
        return set([sl.language for sl 
                    in self.subtitlelanguage_set.filter(
                    is_complete=True).filter(is_original=False)])

    def null_translation_language_codes(self, user):
        null_translations = self.nullsubtitles_set.filter(
            user__id__exact=user.id).filter(
            is_original=False)
        return set([trans.language for trans in null_translations])

    @property
    def writelock_owner_name(self):
        """The user who currently has a subtitling writelock on this video."""
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.__unicode__()

    @property
    def is_writelocked(self):
        """Is this video writelocked for subtitling?"""
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION

    def can_writelock(self, request):
        """Can I place a writelock on this video for subtitling?"""
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        """Writelock this video for subtitling."""
        self._make_writelock(request.user, request.session[VIDEO_SESSION_KEY])
    
    def _make_writelock(self, user, key):
        if user.is_authenticated():
            self.writelock_owner = user
        else:
            self.writelock_owner = None
        self.writelock_session_key = key
        self.writelock_time = datetime.now()        
    
    def release_writelock(self):
        """Writelock this video for subtitling."""
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None

    def notification_list(self, exclude=None):
        if self.subtitle_language():
            return self.subtitle_language().notification_list(exclude)
        else:
            return []

def create_video_id(sender, instance, **kwargs):
    if not instance or instance.video_id:
        return
    alphanum = string.letters+string.digits
    instance.video_id = ''.join([alphanum[random.randint(0, len(alphanum)-1)] 
                                                           for i in xrange(12)])
models.signals.pre_save.connect(create_video_id, sender=Video)

class SubtitleLanguage(models.Model):
    video = models.ForeignKey(Video)
    is_original = models.BooleanField()
    language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255, blank=True)
    writelock_owner = models.ForeignKey(User, null=True)
    is_complete = models.BooleanField(default=False)
    was_complete = models.BooleanField(default=False)
    is_forked = models.BooleanField(default=False)

    class Meta:
        unique_together = (('video', 'language'),)
    
    def __unicode__(self):
        return '%s(%s)' % (self.video, self.language_display())
    
    @models.permalink
    def get_absolute_url(self):
        if self.is_original:
            return ('videos:history', [self.video.video_id])
        else:
            return ('videos:translation_history', [self.video.video_id, self.language])
    
    def language_display(self):
        if self.is_original and not self.language:
            return 'Original'
        return self.get_language_display()

    @property
    def writelock_owner_name(self):
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.__unicode__()

    @property
    def is_writelocked(self):
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION
    
    def can_writelock(self, request):
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        if request.user.is_authenticated():
            self.writelock_owner = request.user
        else:
            self.writelock_owner = None
        self.writelock_session_key = request.session[VIDEO_SESSION_KEY]
        self.writelock_time = datetime.now()

    def release_writelock(self):
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None

    def version(self, version_no=None):
        if version_no is None:
            return self.latest_finished_version()
        try:
            return self.subtitleversion_set.get(version_no=version_no)
        except models.ObjectDoesNotExist:
            pass
    
    def latest_version(self):
        try:
            return self.subtitleversion_set.exclude(time_change=0, text_change=0)[:1].get()
        except models.ObjectDoesNotExist:
            pass        
    
    def latest_finished_version(self):
        """Returns latest SubtitleVersion, or None if none found"""
        try:
            return self.subtitleversion_set.exclude(time_change=0, text_change=0) \
                .filter(finished=True)[:1].get()
        except models.ObjectDoesNotExist:
            pass

    @property
    def percent_done(self):
        if not self.is_original:
            # FIXME: this calculation is incorrect. where are the unit tests?
            # for example, subtitles can be deleted, so it's quite easy 
            # for this to come up with a number greater than 100%
            try:
                translation_count = 0
                for item in self.latest_finished_version().subtitles():
                    if item.subtitle_text:
                        translation_count += 1
            except AttributeError:
                translation_count = 0
            subtitles_count = self.video.version().subtitle_set.count()
            try:
                return int(translation_count / 1. / subtitles_count * 100)
            except ZeroDivisionError:
                return 0 
        else:
            return 0

    def notification_list(self, exclude=None):
        qs = self.subtitleversion_set.all()
        not_send = StopNotification.objects.filter(video=self.video) \
            .values_list('user_id', flat=True)
        for_check = [item.user for item in qs]
        users = []
        for user in for_check:
            if user and user.changes_notification \
                and not user in users and not user.id in not_send \
                and not exclude == user:
                users.append(user)
        return users

class SubtitleCollection(models.Model):
    is_forked=models.BooleanField(default=False)

    class Meta:
        abstract = True

    def subtitles(self):
        if not self.is_dependent():
            return [EffectiveSubtitle.for_subtitle(s)
                    for s in self.subtitle_set.all()]
        else:
            standard_collection = self._get_standard_collection()
            if not standard_collection:
                return []
            else:
                t_dict = \
                    dict([(s.subtitle_id, s) for s
                          in self.subtitle_set.all()])
                subs = [s for s in standard_collection.subtitle_set.all()
                        if s.subtitle_id in t_dict]
                return [EffectiveSubtitle.for_dependent_translation(
                        s, t_dict[s.subtitle_id]) for s in subs]

class SubtitleVersion(SubtitleCollection):
    language = models.ForeignKey(SubtitleLanguage)
    version_no = models.PositiveIntegerField(default=0)
    datetime_started = models.DateTimeField()
    # note: cannot possibly be null for finished SubtitleVersions.
    user = models.ForeignKey(User, null=True)
    note = models.CharField(max_length=512, blank=True)
    time_change = models.FloatField(null=True, blank=True)
    text_change = models.FloatField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-version_no']
        unique_together = (('language', 'version_no'),)
    
    def __unicode__(self):
        return '%s #%s' % (self.language, self.version_no)
    
    @models.permalink
    def get_absolute_url(self):
        return ('videos:revision', [self.pk])

    def is_dependent(self):
        return not self.language.is_original and not self.is_forked
    
    def revision_time(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        d = self.datetime_started.date()
        if d == today:
            return 'Today'
        elif d == yesterday:
            return 'Yesterday'
        else:
            d = d.strftime('%m/%d/%Y')
        return d
    
    def time_change_display(self):
        if not self.time_change:
            return '0%'
        else:
            return '%.0f%%' % (self.time_change*100)

    def text_change_display(self):
        if not self.text_change:
            return '0%'
        else:
            return '%.0f%%' % (self.text_change*100)

    def language_display(self):
        return self.language.language_display()

    @property
    def video(self):
        return self.language.video;

    def update_changes(self):
        old_version = self.prev_version()
        new_subtitles = self.subtitles()
        subtitles_length = len(new_subtitles)

        if not old_version:
            #if it's first version set changes to 100
            self.time_change = 1
            self.text_change = 1          
        elif not subtitles_length:
            self.time_change = 0
            self.text_change = 0
        else:
            old_subtitles = dict([(item.subtitle_id, item) 
                                  for item in old_version.subtitles()])
            time_count_changed, text_count_changed = 0, 0
            #compare subtitless one by one and count changes in time and text
            for subtitle in new_subtitles:
                try:
                    old_subtitle = old_subtitles[subtitle.subtitle_id]
                    if not old_subtitle.subtitle_text == subtitle.subtitle_text:
                        text_count_changed += 1
                    if not old_subtitle.start_time == subtitle.start_time or \
                            not old_subtitle.end_time == subtitle.end_time:
                        time_count_changed += 1
                except KeyError:
                    time_count_changed += 1
                    text_count_changed += 1
            self.time_change = time_count_changed / 1. / subtitles_length
            self.text_change = text_count_changed / 1. / subtitles_length
        self.save()

    def _get_standard_collection(self):
        return self.language.video.latest_finished_version()

    def ordered_subtitles(self):
        return sorted(self.subtitles(), key=lambda item: item.subtitle_order)

    def prev_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__lt=self.version_no) \
                      .filter(language=self.language, finished=True)[:1].get()
        except models.ObjectDoesNotExist:
            pass
        
    def next_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__gt=self.version_no) \
                      .filter(language=self.language, finished=True).order_by('version_no')[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def rollback(self, user):
        cls = self.__class__
        latest_subtitles = self.language.latest_version()
        new_version_no = latest_subtitles.version_no + 1
        note = u'rollback to version #%s' % self.version_no
        new_version = cls(language=self.language, version_no=new_version_no, \
            datetime_started=datetime.now(), user=user, note=note, finished=True)
        new_version.save()
        for item in self.subtitles():
            item.duplicate_for(new_version).save()
        return new_version

    def is_all_blank(self):
        for s in self.subtitles():
            if s.text.strip() != '':
                return False
        return True

post_save.connect(Awards.on_subtitle_version_save, SubtitleVersion)

def update_language_complete_state(sender, instance, created, **kwargs):
    if instance.finished:
        language = instance.language
        if instance.is_all_blank():
            finished_count = language.subtitleversion_set.filter(finished=True).count()
            if finished_count == 1:
                instance.delete()
                language.is_complete = False
                language.was_complete = False
            else:
                subtitles = list(instance.subtitle_set.all())
                for s in subtitles:
                    s.delete()
                language.is_complete = False
                language.was_complete = True
        else:
            language.is_complete = True
            language.was_complete = True
        if language.is_original:
            video = language.video
            video.is_subtitled = language.is_complete
            video.was_subtitled = language.was_complete
            video.save()
        language.save()

post_save.connect(update_language_complete_state, SubtitleVersion)

class NullSubtitles(SubtitleCollection):
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)
    is_original = models.BooleanField()
    language = models.CharField(max_length=16, choices=LANGUAGES, blank=True)

    class Meta:
        unique_together = (('video', 'user', 'language'),)

    def is_dependent(self):
        return not self.is_original and not self.is_forked

    def _get_standard_collection(self):
        return self.video.null_subtitles(self.user, self.language)

class Subtitle(models.Model):
    version = models.ForeignKey(SubtitleVersion, null=True)
    null_subtitles = models.ForeignKey(NullSubtitles, null=True)
    subtitle_id = models.CharField(max_length=32, blank=True)
    subtitle_order = models.FloatField(null=True)
    subtitle_text = models.CharField(max_length=1024, blank=True)
    # in seconds
    start_time = models.FloatField(null=True)
    end_time = models.FloatField(null=True)
    
    class Meta:
        ordering = ['subtitle_order']
        unique_together = (('version', 'subtitle_id'),)
    
    def duplicate_for(self, new_version):
        return Subtitle(version=new_version,
                        subtitle_id=self.subtitle_id,
                        subtitle_order=self.subtitle_order,
                        subtitle_text=self.subtitle_text,
                        start_time=self.start_time,
                        end_time=self.end_time)

    def update_from(self, caption_dict, is_dependent_translation=False):
        self.subtitle_text = caption_dict['text']
        if not is_dependent_translation:
            self.start_time = caption_dict['start_time']
            self.end_time = caption_dict['end_time']

    
class Action(models.Model):
    ADD_VIDEO = 1
    CHANGE_TITLE = 2
    COMMENT = 3
    ADD_VERSION = 4
    TYPES = (
        (ADD_VIDEO, u'add video'),
        (CHANGE_TITLE, u'change title'),
        (COMMENT, u'comment'),
        (ADD_VERSION, u'add version')
    )
    user = models.ForeignKey(User, null=True, blank=True)
    video = models.ForeignKey(Video)
    language = models.ForeignKey(SubtitleLanguage, blank=True, null=True)
    comment = models.ForeignKey(Comment, blank=True, null=True)
    action_type = models.IntegerField(choices=TYPES)
    new_video_title = models.CharField(max_length=2048, blank=True)
    created = models.DateTimeField()
    
    class Meta:
        ordering = ['-created']
        get_latest_by = 'created'
    
    def is_add_version(self):
        return self.action_type == self.ADD_VERSION
    
    def is_comment(self):
        return self.action_type == self.COMMENT
    
    def is_change_title(self):
        return self.action_type == self.CHANGE_TITLE
    
    def is_add_video(self):
        return self.action_type == self.ADD_VIDEO
    
    def type(self):
        if self.comment:
            return 'commented'
        return 'edited'
    
    def time(self):
        if self.created.date() == date.today():
            format = 'g:i A'
        else:
            format = 'g:i A, j M Y'
        return date_format(self.created, format)           
    
    def uprofile(self):
        try:
            return self.user.profile_set.all()[0]
        except IndexError:
            pass        
    
    @classmethod
    def create_comment_handler(cls, sender, instance, created, **kwargs):
        if created:
            model_class = instance.content_type.model_class()
            obj = cls(user=instance.user)
            obj.comment = instance
            obj.created = instance.submit_date
            obj.action_type = cls.COMMENT
            if issubclass(model_class, Video):
                obj.video_id = instance.object_pk
            if issubclass(model_class, SubtitleLanguage):
                obj.language_id = instance.object_pk
                obj.video = instance.content_object.video
            obj.save()
    
    @classmethod
    def create_caption_handler(cls, sender, instance, created, **kwargs):
        if created:
            user = instance.user
            video = instance.language.video
            language = instance.language
            
            obj = cls(user=user, video=video, language=language)
            obj.action_type = cls.ADD_VERSION
            obj.created = instance.datetime_started
            obj.save()            
    
    @classmethod
    def create_video_handler(cls, instance, user):
        video = instance
        obj = cls(user=user, video=video)
        obj.action_type = cls.ADD_VIDEO
        obj.created = datetime.now()
        obj.save()
                
post_save.connect(Action.create_comment_handler, Comment)        
post_save.connect(Action.create_caption_handler, SubtitleVersion)
#post_save.connect(Action.create_video_handler, Video)

class UserTestResult(models.Model):
    email = models.EmailField()
    browser = models.CharField(max_length=1024)
    task1 = models.TextField()
    task2 = models.TextField(blank=True)
    task3 = models.TextField(blank=True)
    get_updates = models.BooleanField(default=False)

class StopNotification(models.Model):
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)
