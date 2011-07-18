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

import logging
logger = logging.getLogger("videos-models")

import string
import random
from datetime import datetime, date, timedelta
import time

from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q
from django.db import IntegrityError
from django.utils.dateformat import format as date_format
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils.http import urlquote_plus, urlquote
from django.utils import simplejson as json
from django.core.urlresolvers import reverse

from gdata.youtube.service import YouTubeService

from auth.models import CustomUser as User, Awards
from videos import EffectiveSubtitle, is_synced, is_synced_value
from videos.types import video_type_registrar
from videos.feed_parser import FeedParser
from comments.models import Comment
from statistic import st_widget_view_statistic
from statistic.tasks import st_sub_fetch_handler_update, st_video_view_handler_update
from widget import video_cache
from utils.redis_utils import RedisSimpleField
from utils.amazon import S3EnabledImageField

from apps.teams. moderation_const import WAITING_MODERATION, APPROVED, MODERATION_STATUSES, UNMODERATED

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
VIDEO_TYPE_BRIGHTCOVE = 'C'
VIDEO_TYPE = (
    (VIDEO_TYPE_HTML5, 'HTML5'),
    (VIDEO_TYPE_YOUTUBE, 'Youtube'),
    (VIDEO_TYPE_BLIPTV, 'Blip.tv'),
    (VIDEO_TYPE_GOOGLE, 'video.google.com'),
    (VIDEO_TYPE_FORA, 'Fora.tv'),
    (VIDEO_TYPE_USTREAM, 'Ustream.tv'),
    (VIDEO_TYPE_VIMEO, 'Vimeo.com'),
    (VIDEO_TYPE_DAILYMOTION, 'dailymotion.com'),
    (VIDEO_TYPE_FLV, 'FLV'),
    (VIDEO_TYPE_BRIGHTCOVE, 'brightcove.com')
)
WRITELOCK_EXPIRATION = 30 # 30 seconds

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

class AlreadyEditingException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __unicode__(self):
        return self.msg
    
class Video(models.Model):
    """Central object in the system"""
    
    video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=2048, blank=True)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text=_(u'in seconds'))
    allow_community_edits = models.BooleanField()
    allow_video_urls_edit = models.BooleanField(default=True)
    writelock_time = models.DateTimeField(null=True, editable=False)
    writelock_session_key = models.CharField(max_length=255, editable=False)
    writelock_owner = models.ForeignKey(User, null=True, editable=False,
                                        related_name="writelock_owners")
    is_subtitled = models.BooleanField(default=False)
    was_subtitled = models.BooleanField(default=False, db_index=True)
    thumbnail = models.CharField(max_length=500, blank=True)
    small_thumbnail = models.CharField(max_length=500, blank=True)
    s3_thumbnail = S3EnabledImageField(blank=True, upload_to='video/thumbnail/')
    edited = models.DateTimeField(null=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followed_videos', editable=False)
    complete_date = models.DateTimeField(null=True, blank=True, editable=False)
    featured = models.DateTimeField(null=True, blank=True)

    subtitles_fetched_count = models.IntegerField(_(u'Sub.fetched'), default=0, db_index=True, editable=False)
    widget_views_count = models.IntegerField(_(u'Widget views'), default=0, db_index=True, editable=False)
    view_count = models.PositiveIntegerField(_(u'Views'), default=0, db_index=True, editable=False)
    
    # Denormalizing the subtitles(had_version) count, in order to get faster joins
    # updated from update_languages_count()
    languages_count = models.PositiveIntegerField(default=0, db_index=True, editable=False)
    moderated_by = models.ForeignKey("teams.Team", blank=True, null=True, related_name="moderating")

    
    def __unicode__(self):
        title = self.title_display()
        if len(title) > 60:
            title = title[:60]+'...'
        return title

    def update_search_index(self):
        from utils.celery_search_index import update_search_index
        update_search_index.delay(self.__class__, self.pk)        
        
    @property
    def views(self):
        if not hasattr(self, '_video_views_statistic'):
            cache_key = 'video_views_statistic_%s' % self.pk
            views_st = cache.get(cache_key)
            
            if not views_st:
                views_st = st_widget_view_statistic.get_views(video=self)
                views_st['total'] = self.widget_views_count
                cache.set(cache_key, views_st, 60*60*2)
                
            self._video_views_statistic = views_st 
            
        return self._video_views_statistic
    
    def title_display(self):
        if self.title:
            return self.title
        
        try:
            url = self.videourl_set.all()[:1].get().url
            if not url:
                return 'No title'
        except models.ObjectDoesNotExist:
            return 'No title'
        
        url = url.strip('/')

        if url.startswith('http://'):
            url = url[7:]

        parts = url.split('/')
        if len(parts) > 1:
            title = '%s/.../%s' % (parts[0], parts[-1])
        else:
            title = url

        if title > 35:
            title = title[:35]+'...'
            
        return title
    
    def update_view_counter(self):
        st_video_view_handler_update.delay(video_id=self.video_id)
    
    def update_subtitles_fetched(self, lang=None):
        st_sub_fetch_handler_update.delay(video_id=self.video_id, sl_pk=lang.pk)
        
        if lang:
            from videos.tasks import update_subtitles_fetched_counter_for_sl
            update_subtitles_fetched_counter_for_sl.delay(sl_pk=lang.pk)
        
    def get_thumbnail(self):
        if self.s3_thumbnail:
            return self.s3_thumbnail.thumb_url(100, 100)
        
        if self.thumbnail:
            return self.thumbnail
        
        return ''
    
    def get_small_thumbnail(self):
        if self.small_thumbnail:
            return self.small_thumbnail
        
        return ''        
    
    @models.permalink
    def video_link(self):
        return ('videos:history', [self.video_id])
    
    def thumbnail_link(self):
        if not self.thumbnail:
            return ''

        if self.thumbnail.startswith('http://'):
            return self.thumbnail
        
        return settings.MEDIA_URL+self.thumbnail
        
    def is_html5(self):
        try:
            return self.videourl_set.filter(original=True)[:1].get().is_html5()
        except models.ObjectDoesNotExist:
            return False
    
    def search_page_url(self):
        return self.get_absolute_url()
    
    def title_for_url(self):
        """
        NOTE: this method is used in videos.search_indexes.VideoSearchResult
        to prevent duplication of code in search result and in DB-query result
        """
        return self.title.replace('/', '-')
    
    def _get_absolute_url(self, locale=None):
        """
        NOTE: this method is used in videos.search_indexes.VideoSearchResult
        to prevent duplication of code in search result and in DB-query result
        
        This is a little hack, because Django uses get_absolute_url in own way,
        so it was impossible just copy to VideoSearchResult
        """        
        kwargs = {}
        if locale:
            kwargs['locale'] = locale 
        title = self.title_for_url()
        if title:
            return reverse('videos:video_with_title', args=[self.video_id, urlquote(title)], kwargs=kwargs)
        return reverse('videos:video', args=[self.video_id], kwargs=kwargs)
    
    get_absolute_url = _get_absolute_url
    
    def get_video_url(self):
        try:
            return self.videourl_set.filter(primary=True).all()[:1].get().effective_url
        except models.ObjectDoesNotExist:
            pass

    @classmethod
    def get_or_create_for_url(cls, video_url=None, vt=None, user=None):
        assert video_url or vt, 'should be video URL or VideoType'
        vt = vt or video_type_registrar.video_type_for_url(video_url)
        if not vt:
            return None, False
        
        try:
            video_url_obj = VideoUrl.objects.get(
                url=vt.convert_to_video_url())
            video, created = video_url_obj.video, False
        except models.ObjectDoesNotExist:
            video, created = None, False
        
        if not video:
            try:
                video_url_obj = VideoUrl.objects.get(
                    type=vt.abbreviation, **vt.create_kwars())
                if user:
                    Action.create_video_handler(video_url_obj.video, user)
                return video_url_obj.video, False
            except models.ObjectDoesNotExist:
                obj = Video()
                obj = vt.set_values(obj)
                if obj.title:
                    obj.slug = slugify(obj.title)
                obj.user = user
                obj.save()
    
                Action.create_video_handler(obj, user)
                
                SubtitleLanguage(video=obj, is_original=True, is_forked=True).save()
                #Save video url
                video_url_obj = VideoUrl()
                if vt.video_id:
                    video_url_obj.videoid = vt.video_id
                video_url_obj.url = vt.convert_to_video_url()
                video_url_obj.type = vt.abbreviation
                video_url_obj.original = True
                video_url_obj.primary = True
                video_url_obj.added_by = user
                video_url_obj.video = obj
                video_url_obj.save()
                
                obj.update_search_index()
                
                video, created = obj, True
        
        user and user.follow_new_video and video.followers.add(user)
        
        return video, created
        
    @property
    def language(self):
        ol = self._original_subtitle_language()

        if ol and ol.language:
            return ol.language
    
    @property
    def filename(self):
        from django.utils.text import get_valid_filename
        
        return get_valid_filename(self.__unicode__())
            
    def lang_filename(self, language):
        name = self.filename
        lang = language.language or u'original'
        return u'%s.%s' % (name, lang)
    
    @property
    def subtitle_state(self):
        """Subtitling state for this video 
        """
        return NO_SUBTITLES if self.latest_version() \
            is None else SUBTITLES_FINISHED

    def _original_subtitle_language(self):
        if not hasattr(self, '_original_subtitle'):
            try:
                original = self.subtitlelanguage_set.filter(is_original=True)[:1].get()
            except models.ObjectDoesNotExist:
                original = None

            setattr(self, '_original_subtitle', original)

        return getattr(self, '_original_subtitle')

    def has_original_language(self):
        original_language = self._original_subtitle_language()
        if original_language:
            return original_language.language != ''

    def subtitle_language(self, language_code=None):
        try:
            if language_code is None:
                return self._original_subtitle_language()
            else:
                return self.subtitlelanguage_set.filter(
                    language=language_code).order_by('-subtitle_count')[:1].get()
        except models.ObjectDoesNotExist:
            return None

    def subtitle_languages(self, language_code):
        return self.subtitlelanguage_set.filter(language=language_code)

    def version(self, version_no=None, language=None, public_only=True):
        if language is None:
            language = self.subtitle_language() 
        return None if language is None else language.version(version_no, public_only=True)

    def latest_version(self, language_code=None, public_only=True):
        language = self.subtitle_language(language_code)
        return None if language is None else language.latest_version(public_only=public_only)

    def subtitles(self, version_no=None, language_code=None, language_pk=None):
        if language_pk is None:
            language = self.subtitle_language(language_code)
        else:
            try:
                language = self.subtitlelanguage_set.get(pk=language_pk)
            except models.ObjectDoesNotExist:
                language = None
        version = self.version(version_no, language)
        if version:
            return version.subtitles()
        else:
            return Subtitle.objects.none()

    def latest_subtitles(self, language_code=None, public_only=True):
        version = self.latest_version(language_code, public_only)
        return [] if version is None else version.subtitles()

    def translation_language_codes(self):
        """All iso language codes with finished translations."""
        return set([sl.language for sl 
                    in self.subtitlelanguage_set.filter(
                    is_complete=True).filter(is_original=False)])

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
        return self.writelock_session_key == \
            request.browser_id or \
            not self.is_writelocked

    def writelock(self, request):
        """Writelock this video for subtitling."""
        self._make_writelock(request.user, request.browser_id)
    
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
        qs = self.followers.filter(changes_notification=True, is_active=True)
        if exclude:
            if not isinstance(exclude, (list, tuple)):
                exclude = [exclude]
            qs = qs.exclude(pk__in=[u.pk for u in exclude if u and u.is_authenticated()])
        return qs    
    
    def notification_list_all(self, exclude=None):
        users = []
        for language in self.subtitlelanguage_set.all():
            for u in language.notification_list(exclude):
                if not u in users:
                    users.append(u) 
        for user in self.notification_list(exclude):
            if not user in users: 
                users.append(user)                    
        return users

    def subtitle_language_dict(self):
        langs = {}
        for sl in self.subtitlelanguage_set.all():
            if not sl.language:
                continue
            if sl.language in langs:
                langs[sl.language].append(sl)
            else:
                langs[sl.language] = [sl]
        return langs    
                                                    
    @property
    def is_complete(self):
        """
        We consider complete a video which has one or more
        subtitle languages either marked as complete, or 
        having 100%  as the percent_done.
        """
        for sl in self.subtitlelanguage_set.all():
            if sl.is_complete_and_synced():
                return True
        return False

    def completed_subtitle_languages(self):
        return [sl for sl 
                in self.subtitlelanguage_set.all()
                if sl.is_complete_and_synced()]


    @property
    def is_moderated(self):
        return bool(self.moderated_by_id)
    
    class Meta(object):
        permissions = (
            ("can_moderate_version"   , "Can moderate version" ,),
        )

def create_video_id(sender, instance, **kwargs):
    instance.edited = datetime.now()
    if not instance or instance.video_id:
        return
    alphanum = string.letters+string.digits
    instance.video_id = ''.join([alphanum[random.randint(0, len(alphanum)-1)] 
                                 for i in xrange(12)])
    
def video_delete_handler(sender, instance, **kwargs):
    video_cache.invalidate_cache(instance.video_id)

models.signals.pre_save.connect(create_video_id, sender=Video)
models.signals.pre_delete.connect(video_delete_handler, sender=Video)
models.signals.m2m_changed.connect(User.video_followers_change_handler, sender=Video.followers.through)

class SubtitleLanguage(models.Model):
    
    video = models.ForeignKey(Video)
    is_original = models.BooleanField()
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES, blank=True)
    writelock_time = models.DateTimeField(null=True, editable=False)
    writelock_session_key = models.CharField(max_length=255, blank=True, editable=False)
    writelock_owner = models.ForeignKey(User, null=True, blank=True, editable=False)
    is_complete = models.BooleanField(default=False)
    subtitle_count = models.IntegerField(default=0, editable=False)
    has_version = models.BooleanField(default=False, editable=False)
    had_version = models.BooleanField(default=False, editable=False)
    is_forked = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    subtitles_fetched_count = models.IntegerField(default=0, editable=False)
    followers = models.ManyToManyField(User, blank=True, related_name='followed_languages', editable=False)
    title = models.CharField(max_length=2048, blank=True)
    percent_done = models.IntegerField(default=0, editable=False)
    standard_language = models.ForeignKey('self', null=True, blank=True, editable=False)

    subtitles_fetched_counter = RedisSimpleField()

    class Meta:
        unique_together = (('video', 'language', 'standard_language'),)
    
    def __unicode__(self):
        return self.language_display()
    
    def nonblank_subtitle_count(self):
        return len([s for s in self.latest_subtitles() if s.text])
    
    def get_title_display(self):
        return self.get_title() or self.video.title
        
    def get_title(self):
        if self.is_original:
            return self.video.title
        
        return self.title
    
    def is_dependent(self):
        return not self.is_original and not self.is_forked

    def is_complete_and_synced(self):
        if not self.is_dependent() and not self.is_complete:
            return False
        if self.is_dependent():
            if self.percent_done != 100:
                return False
            standard_lang = self.real_standard_language()
            if not standard_lang or not standard_lang.is_complete:
                return False
        subtitles = self.latest_subtitles()
        if len(subtitles) == 0:
            return False
        if len([s for s in subtitles[:-1] if not s.has_complete_timing()]) > 0:
            return False
        if not is_synced_value(subtitles[-1].start_time):
            return False
        return True

    def real_standard_language(self):
        if self.standard_language:
            return self.standard_language
        elif self.is_dependent():
            # This should only be needed temporarily until data is more cleaned up.
            # in other words, self.standard_language should never be None for a dependent SL
            try:
                self.standard_language = self.video.subtitle_language()
                self.save()
                return self.standard_language
            except IntegrityError:
                logger.error(
                    "Subtitle Language {0} is dependent but has no acceptable "
                    "standard_language".format(self.id))
        return None

    def is_dependable(self):
        if self.is_dependent():
            dep_lang = self.real_standard_language()
            return dep_lang and dep_lang.is_complete and self.percent_done > 10
        else:
            return self.is_complete

    def get_widget_url(self):
        # duplicates mirosubs.widget.SubtitleDialogOpener.prototype.openDialogOrRedirect_
        video = self.video
        video_url = video.get_video_url()
        config = {
            "videoID": video.video_id,
            "videoURL": video_url,
            "effectiveVideoURL": video_url,
            "languageCode": self.language,
            "subLanguagePK": self.pk,
            "originalLanguageCode": video.language }
        if self.is_dependent():
            config['baseLanguagePK'] = self.standard_language and self.standard_language.pk
        return reverse('onsite_widget')+'?config='+urlquote_plus(json.dumps(config))

    @models.permalink
    def get_absolute_url(self):
        if self.is_original:
            return  ('videos:history', [self.video.video_id])
        else:
            return  ('videos:translation_history', [self.video.video_id, self.language, self.pk])

    
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
        return self.writelock_session_key == \
            request.browser_id or \
            not self.is_writelocked

    def writelock(self, request):
        if request.user.is_authenticated():
            self.writelock_owner = request.user
        else:
            self.writelock_owner = None
        self.writelock_session_key = request.browser_id
        self.writelock_time = datetime.now()

    def release_writelock(self):
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None        

    def _filter_public(self, versions, public_only):
        from apps.teams.moderation import  APPROVED, UNMODERATED
        if public_only:
            versions = versions.filter( moderation_status__in=[APPROVED, UNMODERATED])
        return versions    
        
    def version(self, version_no=None, public_only=True):
        if version_no is None:
            return self.latest_version(public_only)
        try:
            return self._filter_public( self.subtitleversion_set.filter(version_no=version_no), public_only)[0]
        except (models.ObjectDoesNotExist, IndexError):
            pass

    @property    
    def last_version(self):
        return self.latest_version(public_only=True)
    
    def latest_version(self, public_only=True):
        try:
            return self._filter_public( self.subtitleversion_set.all(), public_only)[0]
        except (SubtitleVersion.DoesNotExist, IndexError):
            return None
    
    def latest_subtitles(self):
        version = self.latest_version()
        if version:
            return version.subtitles()
        return []

    def notification_list(self, exclude=None):
        qs = self.followers.filter(changes_notification=True, is_active=True)

        if exclude:
            if not isinstance(exclude, (list, tuple)):
                exclude = [exclude]            
            qs = qs.exclude(pk__in=[u.pk for u in exclude if u])
        return qs

    def translations(self):
        return SubtitleLanguage.objects.filter(video=self.video, is_original=False, is_forked=False)

    def fork(self, from_version=None, user=None, result_of_rollback=False, attach_to_language=None):
        """
        If this a dependent and non write locked language,
        then will fork it, making all it's subs timing not
        depend on anything else.
        If locked, will throw an AlreadyEditingException .
        If attach_to_language is passed, we will copy those
        subs to a new language, else self will be used
        """
        to_language = attach_to_language or self
        if from_version:
            original_subs = from_version.subtitle_set.all()
        else:
            if self.standard_language is None:
                return    
            original_subs = self.standard_language.latest_version().subtitle_set.all()        
        
        if self.is_writelocked:
            raise AlreadyEditingException(_("Sorry, you cannot upload subtitles right now because someone is editing the language you are uploading or a translation of it"))
        try:
            old_version = self.subtitleversion_set.all()[:1].get()    
            version_no = old_version.version_no + 1
        except SubtitleVersion.DoesNotExist:
            old_version = None
            version_no = 0

        version = SubtitleVersion(
                language=to_language, version_no=version_no,
                datetime_started=datetime.now(), user=user,
                note=u'Uploaded', is_forked=True, time_change=1, text_change=1, result_of_rollback=result_of_rollback)
        version.save()

        if old_version:
            original_sub_dict = dict([(s.subtitle_id, s) for s  in original_subs])
            my_subs = old_version.subtitle_set.all()
            for sub in my_subs:
                if sub.subtitle_id in original_sub_dict:
                    # if we can match, then we can simply copy
                    # time data
                    standard_sub = original_sub_dict[sub.subtitle_id]
                    sub.start_time = standard_sub.start_time
                    sub.end_time = standard_sub.end_time
                    sub.subtitle_order = standard_sub.subtitle_order
                sub.pk = None
                sub.version = version
                sub.save()

        self.is_forked = True
        self.standard_language = None
        self.save()

models.signals.m2m_changed.connect(User.sl_followers_change_handler, sender=SubtitleLanguage.followers.through)


class SubtitleCollection(models.Model):
    is_forked=models.BooleanField(default=False)
    # should not be changed directly, but using teams.moderation. as those will take care
    # of keeping the state constant and also updating metadata when needed
    moderation_status = models.CharField(max_length=32, choices=MODERATION_STATUSES ,
                                         default=UNMODERATED, db_index=True)
    
    class Meta:
        abstract = True

                        
    def subtitles(self, subtitles_to_use=None):
        ATTR = 'computed_effective_subtitles'
        if hasattr(self, ATTR):
            return getattr(self, ATTR)
        if  self.pk:
            # if this collection hasn't been saved, then subtitle_set.all will return all subtitles
            # which will take too long / never return
            subtitles = subtitles_to_use or self.subtitle_set.all()
        else:
            subtitles = subtitles_to_use or []
        if not self.is_dependent():
            effective_subtitles = [EffectiveSubtitle.for_subtitle(s)
                                   for s in subtitles]
        else:
            standard_collection = self._get_standard_collection()
            if not standard_collection:
                effective_subtitles = []
            else:
                t_dict = \
                    dict([(s.subtitle_id, s) for s
                          in subtitles])
                filtered_subs = standard_collection.subtitle_set.all()
                subs = [s for s in filtered_subs
                        if s.subtitle_id in t_dict]
                effective_subtitles = \
                    [EffectiveSubtitle.for_dependent_translation(
                        s, t_dict[s.subtitle_id]) for s in subs]
        setattr(self, ATTR, effective_subtitles)
        return effective_subtitles

class SubtitleVersion(SubtitleCollection):
    language = models.ForeignKey(SubtitleLanguage)
    version_no = models.PositiveIntegerField(default=0)
    datetime_started = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, null=True)
    note = models.CharField(max_length=512, blank=True)
    time_change = models.FloatField(null=True, blank=True, editable=False)
    text_change = models.FloatField(null=True, blank=True, editable=False)
    notification_sent = models.BooleanField(default=False)
    result_of_rollback = models.BooleanField(default=False)



    class Meta:
        ordering = ['-version_no']
        unique_together = (('language', 'version_no'),)
    
    def __unicode__(self):
        return u'%s #%s' % (self.language, self.version_no)
    
    def save(self, *args, **kwargs):
        created = not self.pk
        if created and self.language.video.is_moderated:
            self.moderation_status  = WAITING_MODERATION
        super(SubtitleVersion, self).save(*args, **kwargs)
        if created:
            #but some bug happen, I've no idea why
            Action.create_caption_handler(self)
            if self.user:
                video = self.language.video
                has_other_versions = SubtitleVersion.objects.filter(language__video=video) \
                    .filter(user=self.user).exclude(pk=self.pk).exists()
                
                if not has_other_versions:
                    video.followers.add(self.user)

    def changed_from(self, other_subs):
        my_subs = self.subtitles()
        if len(other_subs) != len(my_subs):
            return True
        pairs = zip(my_subs, other_subs)
        for pair in pairs:
            if pair[0].text != pair[1].text or \
                    pair[0].start_time != pair[1].start_time or \
                    pair[0].end_time != pair[1].end_time:
                return True
        return False

    def has_subtitles(self):
        return self.subtitle_set.exists()
    
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
            return '%.0f%%' % (self.time_change * 100)

    def text_change_display(self):
        if not self.text_change:
            return '0%'
        else:
            return '%.0f%%' % (self.text_change * 100)

    def language_display(self):
        return self.language.language_display()

    @property
    def video(self):
        return self.language.video;

    def _get_standard_collection(self):
        standard_language = self.language.real_standard_language()
        if standard_language:
            return standard_language.latest_version()

    def ordered_subtitles(self):
        subtitles = self.subtitles()
        subtitles.sort(key=lambda item: item.sub_order)
        return subtitles

    def prev_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__lt=self.version_no) \
                      .filter(language=self.language) \
                      .exclude(text_change=0, time_change=0)[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def next_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__gt=self.version_no) \
                      .filter(language=self.language) \
                      .exclude(text_change=0, time_change=0) \
                      .order_by('version_no')[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def rollback(self, user):
        cls = self.__class__
        #to be sure we have real data in instance, without cached values in attributes
        lang = SubtitleLanguage.objects.get(id=self.language.id) 
        latest_subtitles = lang.latest_version(public_only=False)
        new_version_no = latest_subtitles.version_no + 1
        note = u'rollback to version #%s' % self.version_no

        if latest_subtitles.result_of_rollback is False:
            # if we have tanslations, we need to keep a forked version of them
            # else all translations will be wiped by an earlier original rollback
            for translation in self.language.translations():            
                if len(translation.latest_subtitles()) > 0:
                    try:
                        # this can fail, because if we already have a forked subs with this lang
                        # we will hit the db unique constraint
                        translation.fork(result_of_rollback=True)
                    except IntegrityError:
                        raise
                        logger.warning(
                            "Got error on forking insinde rollback, original %s, forked %s" %
                            (lang.pk, translation.pk))
        new_version = cls(language=lang, version_no=new_version_no, \
                              datetime_started=datetime.now(), user=user, note=note, 
                          is_forked=self.is_forked,
                          result_of_rollback=True)
        new_version.save()
        
        for item in self.subtitle_set.all():
            item.duplicate_for(version=new_version).save()
        self.latest_version = new_version
        return new_version

    def is_all_blank(self):
        for s in self.subtitles():
            if s.text.strip() != '':
                return False
        return True

def update_followers(sender, instance, created, **kwargs):
    user = instance.user
    lang = instance.language
    if created and user and user.changes_notification:
        if not SubtitleVersion.objects.filter(user=user).exists():
            #If user edited before it should be in followers, or removed yourself, 
            #so we should not add again
            lang.followers.add(instance.user)
            lang.video.followers.add(instance.user)

post_save.connect(Awards.on_subtitle_version_save, SubtitleVersion)
post_save.connect(update_followers, SubtitleVersion)

class SubtitleDraft(SubtitleCollection):
    language = models.ForeignKey(SubtitleLanguage)
    # null iff there is no SubtitleVersion yet.
    parent_version = models.ForeignKey(SubtitleVersion, null=True)
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    browser_id = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=2048, blank=True)
    last_saved_packet = models.PositiveIntegerField(default=0)

    @property
    def version_no(self):
        return 0 if self.parent_version is None else \
            self.parent_version.version_no + 1

    @property
    def video(self):
        return self.language.video

    def _get_standard_collection(self):
        if self.language.standard_language:
            return self.language.standard_language.latest_version()
        else:
            return self.language.video.latest_version()

    def is_dependent(self):
        return not self.language.is_original and not self.is_forked

    def matches_request(self, request):
        if request.user.is_authenticated() and self.user and \
                self.user.pk == request.user.pk:
            return True
        else:
            return request.browser_id == self.browser_id

class SubtitleManager(models.Manager):

    def unsynced(self):
        return self.get_query_set().filter(start_time__isnull=True, end_time__isnull=True)
        
class Subtitle(models.Model):
    version = models.ForeignKey(SubtitleVersion, null=True)
    draft = models.ForeignKey(SubtitleDraft, null=True)
    subtitle_id = models.CharField(max_length=32, blank=True)
    subtitle_order = models.FloatField(null=True)
    subtitle_text = models.CharField(max_length=1024, blank=True)
    # in seconds
    start_time = models.FloatField(null=True)
    end_time = models.FloatField(null=True)

    objects = SubtitleManager()
    
    class Meta:
        ordering = ['subtitle_order']
        unique_together = (('version', 'subtitle_id'), ('draft', 'subtitle_id'),)

    @property
    def is_synced(self):
        return is_synced(self)
    
    def duplicate_for(self, version=None, draft=None):
        return Subtitle(version=version,
                        draft=draft,
                        subtitle_id=self.subtitle_id,
                        subtitle_order=self.subtitle_order,
                        subtitle_text=self.subtitle_text,
                        start_time=self.start_time,
                        end_time=self.end_time)
    
    @classmethod
    def trim_list(cls, subtitles):
        first_nonblank_index = -1
        last_nonblank_index = -1
        index = -1
        for subtitle in subtitles:
            index += 1
            if subtitle.subtitle_text.strip() != '':
                if first_nonblank_index == -1:
                    first_nonblank_index = index
                last_nonblank_index = index
        if first_nonblank_index != -1:
            return subtitles[first_nonblank_index:last_nonblank_index + 1]
        else:
            return []

    def update_from(self, caption_dict, is_dependent_translation=False):
        if 'text' in caption_dict:
            self.subtitle_text = caption_dict['text']

        if not is_dependent_translation:
            if 'start_time' in caption_dict:
                self.start_time = caption_dict['start_time']
                
            if 'end_time' in caption_dict:
                self.end_time = caption_dict['end_time']

    def save(self, *args, **kwargs):
        if not self.is_synced:
            self.start_time = self.end_time = None
        return super(Subtitle, self).save(*args, **kwargs)
        
    def __unicode__(self):
        if self.pk:
            return u"(%4s) %s %s -> %s - syc = %s = %s -- Version %s" % (self.subtitle_order, self.subtitle_id,
                                          self.start_time, self.end_time, self.is_synced, self.subtitle_text, self.version_id)
    
from django.template.loader import render_to_string

class ActionRenderer(object):
    
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, item):
        if item.action_type == Action.ADD_VIDEO:
            info = self.redner_ADD_VIDEO(item)
        elif item.action_type == Action.CHANGE_TITLE:
            info = self.redner_CHANGE_TITLE(item)
        elif item.action_type == Action.COMMENT:
            info = self.redner_COMMENT(item)
        elif item.action_type == Action.ADD_VERSION:
            info = self.render_ADD_VERSION(item)
        elif item.action_type == Action.ADD_VIDEO_URL:
            info = self.redner_ADD_VIDEO_URL(item)
        elif item.action_type == Action.ADD_TRANSLATION:
            info = self.render_ADD_TRANSLATION(item)
        elif item.action_type == Action.SUBTITLE_REQUEST:
            info = self.render_SUBTITLE_REQUEST(item)

        else:
            info = ''
        
        context = {
            'info': info,
            'item': item
        }
        
        return render_to_string(self.template_name, context)
    
    def _base_kwargs(self, item):
        return {
            'video_url': item.video.get_absolute_url(),
            'video_name': unicode(item.video)                  
        }
            
    def redner_ADD_VIDEO(self, item):
        if item.user:
            msg = _(u'added video <a href="%(video_url)s">%(video_name)s</a>') 
        else:
            msg = _(u'<a href="%(video_url)s">%(video_name)s</a> video added') 
        
        return msg % self._base_kwargs(item)
        
    def redner_CHANGE_TITLE(self, item):
        if item.user:
            msg = _(u'changed title for <a href="%(video_url)s">%(video_name)s</a>') 
        else:
            msg = _(u'Title was changed for <a href="%(video_url)s">%(video_name)s</a>') 
        
        return msg % self._base_kwargs(item)
    
    def redner_COMMENT(self, item):
        kwargs = self._base_kwargs(item)
        
        if item.language:
            kwargs['comments_url'] = '%s#comments' % item.language.get_absolute_url()
            kwargs['language'] = item.language.language_display()
        else:
            kwargs['comments_url'] = '%s#comments' % kwargs['video_url']
        
        if item.language:
            if item.user:
                msg = _(u'commented on <a href="%(comments_url)s">%(language)s subtitles</a> for <a href="%(video_url)s">%(video_name)s</a>')
            else:
                msg = _(u'Comment added for <a href="%(comments_url)s">%(language)s subtitles</a> for <a href="%(video_url)s">%(video_name)s</a>')
        else:
            if item.user:
                msg = _(u'commented on <a href="%(video_url)s">%(video_name)s</a>')
            else:
                msg = _(u'Comment added for <a href="%(video_url)s">%(video_name)s</a>')
            
        return msg % kwargs
    
    def render_ADD_TRANSLATION(self, item):
        kwargs = self._base_kwargs(item)
        
        kwargs['language'] = item.language.language_display()
        kwargs['language_url'] = item.language.get_absolute_url()
        
        if item.user:
            msg = _(u'started <a href="%(language_url)s">%(language)s subtitles</a> for <a href="%(video_url)s">%(video_name)s</a>')
        else:
            msg = _(u'<a href="%(language_url)s">%(language)s subtitles</a> started for <a href="%(video_url)s">%(video_name)s</a>')
        
        return msg % kwargs
        
    def render_ADD_VERSION(self, item):
        kwargs = self._base_kwargs(item)
        
        kwargs['language'] = item.language.language_display()
        kwargs['language_url'] = item.language.get_absolute_url()
        
        if item.user:
            msg = _(u'edited <a href="%(language_url)s">%(language)s subtitles</a> for <a href="%(video_url)s">%(video_name)s</a>')
        else:
            msg = _(u'<a href="%(language_url)s">%(language)s subtitles</a> edited for <a href="%(video_url)s">%(video_name)s</a>')
        
        return msg % kwargs
    
    def redner_ADD_VIDEO_URL(self, item):
        if item.user:
            msg = _(u'added new URL for <a href="%(video_url)s">%(video_name)s</a>') 
        else:
            msg = _(u'New URL added for <a href="%(video_url)s">%(video_name)s</a>') 
        
        return msg % self._base_kwargs(item)

    def render_SUBTITLE_REQUEST(self, item):
        requests = item.subtitlerequests.all()
        languages = [request.get_language_display() for request in requests]
        kwargs = self._base_kwargs(item)
        kwargs['languages'] = ', '.join(languages)

        if item.user:
            msg = _(u'requested subtitles for <a href="%(video_url)s">%(video_name)s</a> in %(languages)s.')
        else:
            msg = _(u'New subtitles requested for <a href="%(video_url)s">%(video_name)s</a> in %(languages)s.')

        return msg % kwargs

class Action(models.Model):
    ADD_VIDEO = 1
    CHANGE_TITLE = 2
    COMMENT = 3
    ADD_VERSION = 4
    ADD_VIDEO_URL = 5
    ADD_TRANSLATION = 6
    SUBTITLE_REQUEST = 7
    APPROVE_VERSION = 8
    TYPES = (
        (ADD_VIDEO, _(u'add video')),
        (CHANGE_TITLE, _(u'change title')),
        (COMMENT, _(u'comment')),
        (ADD_VERSION, _(u'add version')),
        (ADD_TRANSLATION, _(u'add translation')),
        (ADD_VIDEO_URL, _(u'add video url')),
        (SUBTITLE_REQUEST, _(u'request subtitles')),
        (APPROVE_VERSION, _(u'approve version')),
    )
    
    renderer = ActionRenderer('videos/_action_tpl.html')
    renderer_for_video = ActionRenderer('videos/_action_tpl_video.html')
    
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
    
    def __unicode__(self):
        u = self.user and self.user.__unicode__() or 'Anonymous'
        return u'%s: %s(%s)' % (u, self.get_action_type_display(), self.created)
    
    def render(self, renderer=None):
        if not renderer:
            renderer = self.renderer
            
        return renderer.render(self)
    
    def render_for_video(self):
        return self.render(self.renderer_for_video)
    
    def is_add_video_url(self):
        return self.action_type == self.ADD_VIDEO_URL
    
    def is_add_version(self):
        return self.action_type == self.ADD_VERSION
    
    def is_comment(self):
        return self.action_type == self.COMMENT
    
    def is_change_title(self):
        return self.action_type == self.CHANGE_TITLE
    
    def is_add_video(self):
        return self.action_type == self.ADD_VIDEO
    
    def type(self):
        if self.comment_id:
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
    def change_title_handler(cls, video, user):
        action = cls(new_video_title=video.title, video=video)
        action.user = user.is_authenticated() and user or None
        action.created = datetime.now()
        action.action_type = cls.CHANGE_TITLE
        action.save()
    
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
    def create_caption_handler(cls, instance):
        user = instance.user
        video = instance.language.video
        language = instance.language
        
        obj = cls(user=user, video=video, language=language)
        
        if instance.version_no == 0:
            obj.action_type = cls.ADD_TRANSLATION
        else:
            obj.action_type = cls.ADD_VERSION
            
        obj.created = instance.datetime_started
        obj.save()            
    
    @classmethod
    def create_video_handler(cls, video, user=None):
        obj = cls(video=video)
        obj.action_type = cls.ADD_VIDEO
        obj.user = user
        obj.created = datetime.now()
        obj.save()
     
    @classmethod
    def create_video_url_handler(cls, sender, instance, created, **kwargs):
        if created and instance.video_id and sender.objects.filter(video=instance.video).count() > 1:
            obj = cls(video=instance.video)
            obj.user = instance.added_by
            obj.action_type = cls.ADD_VIDEO_URL
            obj.created = instance.created
            obj.save()

    @classmethod
    def create_approved_video_handler(cls, version, moderator,  **kwargs):
        obj = cls(video=version.video)
        obj.language = version.language
        obj.user = moderator
        obj.action_type = cls.APPROVE_VERSION
        obj.created = datetime.now()
        obj.save()

                
post_save.connect(Action.create_comment_handler, Comment)        

class UserTestResult(models.Model):
    email = models.EmailField()
    browser = models.CharField(max_length=1024)
    task1 = models.TextField()
    task2 = models.TextField(blank=True)
    task3 = models.TextField(blank=True)
    get_updates = models.BooleanField(default=False)

class VideoUrl(models.Model):
    video = models.ForeignKey(Video)
    type = models.CharField(max_length=1, choices=VIDEO_TYPE)
    url = models.URLField(max_length=255, unique=True)
    videoid = models.CharField(max_length=50, blank=True)
    primary = models.BooleanField(default=False)
    original = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return self.url
    
    def is_html5(self):
        return self.type == VIDEO_TYPE_HTML5
    
    @models.permalink
    def get_absolute_url(self):
        return ('videos:video_url', [self.video.video_id, self.pk])
    
    def unique_error_message(self, model_class, unique_check):
        if unique_check[0] == 'url':
            vu_obj = VideoUrl.objects.get(url=self.url)
            return mark_safe(_('This URL already <a href="%(url)s">exists</a> as its own video in our system. You can\'t add it as a secondary URL.') % {'url': vu_obj.get_absolute_url()})
        return super(VideoUrl, self).unique_error_message(model_class, unique_check)
    
    def created_as_time(self):
        #for sorting in js
        return time.mktime(self.created.timetuple())

    @property
    def effective_url(self):
        return video_type_registrar[self.type].video_url(self)

post_save.connect(Action.create_video_url_handler, VideoUrl)   
post_save.connect(video_cache.on_video_url_save, VideoUrl)

class VideoFeed(models.Model):
    url = models.URLField()
    last_link = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return self.url
    
    def update(self):
        feed_parser = FeedParser(self.url)
        
        checked_entries = 0
        last_link = self.last_link
        
        try:
            self.last_link = feed_parser.feed.entries[0]['link']
            self.save()
        except (IndexError, KeyError):
            pass       
        
        _iter = feed_parser.items(reverse=True, until=last_link, ignore_error=True)
        
        for vt, info, entry in _iter:
            vt and Video.get_or_create_for_url(vt=vt, user=self.user)
            checked_entries += 1
        
        return checked_entries

