
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

from django.db.models import ObjectDoesNotExist
from videos import models
from widget.models import SubtitlingSession
from datetime import datetime
import re
import simplejson as json
import widget
from widget.base_rpc import BaseRpc
from urlparse import urlparse, parse_qs
from django.conf import settings
from django.db.models import Sum
from widget import video_cache
from utils.translation import get_user_languages_from_request
from django.utils.translation import ugettext as _
from subrequests.models import SubtitleRequest
from uslogging.models import WidgetDialogLog
from videos.tasks import video_changed_tasks


from utils import send_templated_email
from statistic.tasks import st_widget_view_statistic_update
import logging
yt_logger = logging.getLogger("youtube-ei-error")

ALL_LANGUAGES = settings.ALL_LANGUAGES
LANGUAGES_MAP = dict(ALL_LANGUAGES)

def add_general_settings(request, dict):
    dict.update({
            'writelock_expiration' : models.WRITELOCK_EXPIRATION,
            'embed_version': settings.EMBED_JS_VERSION,
            'languages': ALL_LANGUAGES,
            'metadata_languages': settings.METADATA_LANGUAGES
            })
    if request.user.is_authenticated():
        dict['username'] = request.user.username

class Rpc(BaseRpc):
    def log_session(self, request, draft_pk, log):
        dialog_log = WidgetDialogLog(
            draft_pk=draft_pk,
            browser_id=request.browser_id,
            log=log)
        dialog_log.save()
        send_templated_email(
            settings.WIDGET_LOG_EMAIL,
            'Subtitle save failure',
            'widget/session_log_email.txt',
            { 'log_pk': dialog_log.pk },
            fail_silently=False)
        return { 'response': 'ok' }

    def log_youtube_ei_failure(self, request, page_url):
        user_agent = request.META.get('HTTP_USER_AGENT', '(Unknown)')
        yt_logger.error(
            "Youtube ExternalInterface load failure",
            extra={
                'request': request,
                'data': {
                    'user_agent': user_agent,
                    'page_url': page_url }
                })
        return { 'response': 'ok' }

    def show_widget(self, request, video_url, is_remote, base_state=None, additional_video_urls=None):
        video_id = video_cache.get_video_id(video_url)

        if video_id is None: # for example, private youtube video.
            return None

        try:    
            video_urls = video_cache.get_video_urls(video_id)
        except models.Video.DoesNotExist:
            video_cache.invalidate_video_id(video_url)
            video_id = video_cache.get_video_id(video_url)
            video_urls = video_cache.get_video_urls(video_id)

        return_value = {
            'video_id' : video_id,
            'subtitles': None,
        }
        return_value['video_urls']= video_urls
        return_value['is_moderated'] = video_cache.get_is_moderated(video_id)
        if additional_video_urls is not None:
            for url in additional_video_urls:
                video_cache.associate_extra_url(url, video_id)

        st_widget_view_statistic_update.delay(video_id=video_id)
        
        add_general_settings(request, return_value)
        if request.user.is_authenticated():
            return_value['username'] = request.user.username

        return_value['drop_down_contents'] = \
            video_cache.get_video_languages(video_id)

        if base_state is not None and base_state.get("language_code", None) is not None:
            lang_pk = base_state.get('language_pk', None)
            if lang_pk is  None:
                lang_code = base_state.get('language_code', None)
                lang_pk = video_cache.pk_for_default_language(video_id, lang_code)
            subtitles = self._autoplay_subtitles(
                request.user, video_id, 
                lang_pk,
                base_state.get('revision', None))
            return_value['subtitles'] = subtitles
        else:
            if is_remote:
                autoplay_language = self._find_remote_autoplay_language(request)
                language_pk = video_cache.pk_for_default_language(video_id, autoplay_language)
                if autoplay_language is not None:
                    subtitles = self._autoplay_subtitles(
                        request.user, video_id, language_pk, None)
                    return_value['subtitles'] = subtitles
        return return_value

    def fetch_start_dialog_contents(self, request, video_id):
        my_languages = get_user_languages_from_request(request)
        my_languages.extend([l[:l.find('-')] for l in my_languages if l.find('-') > -1])
        video = models.Video.objects.get(video_id=video_id)
        video_languages = [language_summary(l) for l 
                           in video.subtitlelanguage_set.all()]
        original_language = None
        if video.subtitle_language():
            original_language = video.subtitle_language().language
        return {
            'my_languages': my_languages,
            'video_languages': video_languages,
            'original_language': original_language }

    def fetch_video_id_and_settings(self, request, video_id):
        is_original_language_subtitled = self._subtitle_count(video_id) > 0
        general_settings = {}
        add_general_settings(request, general_settings)
        return {
            'video_id': video_id,
            'is_original_language_subtitled': is_original_language_subtitled,
            'general_settings': general_settings }

    def fetch_request_dialog_contents(self, request, video_id):
        '''
        Fetch the contents for creating a dialog to create request subtitles
        form.
        '''
        my_languages = get_user_languages_from_request(request)
        my_languages.extend([l[:l.find('-')] for l in my_languages if l.find('-') > -1])

        # List of language-code tuples
        all_languages = sorted(LANGUAGES_MAP.items())

        ##TODO: Filter all_languages according to already submitted requests
        # after creation of SubtitleRequest Model

        return {
            'my_languages': my_languages,
            'all_languages': all_languages
        }

    def submit_subtitle_request(self, request, video_id, request_languages, track_request,
                                description):
        '''
        Processes a request submitted through the UI
        '''
        status = True
        message = ''

        subreqs = SubtitleRequest.objects.create_requests(
                video_id,
                request.user,
                request_languages,
                track=track_request,
        )

        return {
            'status':status,
            'message': message,
            'count' : len(subreqs),
        }

    def start_editing(self, request, video_id, 
                      language_code, 
                      subtitle_language_pk=None,
                      base_language_pk=None,
                      original_language_code=None):
        """Called by subtitling widget when subtitling or translation 
        is to commence on a video.
        """
        # TODO: remove whenever blank SubtitleLanguages become illegal.
        self._fix_blank_original(video_id)
        if language_code == original_language_code:
            base_language_pk = None
        base_language = None
        if base_language_pk is not None:
            base_language = models.SubtitleLanguage.objects.get(
                pk=base_language_pk)

        language, can_edit = self._get_language_for_editing(
            request, video_id, language_code, 
            subtitle_language_pk, base_language)

        if not can_edit:
            return { "can_edit": False, 
                     "locked_by" : language.writelock_owner_name }

        session = self._make_subtitling_session(
            request, language, base_language)
        version_for_subs = language.version()
        if not version_for_subs:
            version_for_subs = self._create_version_from_session(session)
            version_no = 0
        else:
            version_no = version_for_subs.version_no + 1
        subtitles = self._subtitles_dict(
            version_for_subs, version_no, base_language_pk is None)
        return_dict = { "can_edit" : True,
                        "session_pk" : session.pk,
                        "subtitles" : subtitles }
        if base_language:
            return_dict['original_subtitles'] = \
                self._subtitles_dict(base_language.latest_version())
        if original_language_code:
            self._save_original_language(video_id, original_language_code)
        video_cache.writelock_add_lang(video_id, language.language)
        return return_dict

    def resume_editing(self, request, session_pk):
        session = SubtitlingSession.objects.get(pk=session_pk)
        if session.language.can_writelock(request) and \
                session.parent_version == session.language.version():
            session.language.writelock(request)
            # FIXME: Duplication between this and start_editing.
            version_for_subs = session.language.version()
            if not version_for_subs:
                version_for_subs = self._create_version_from_session(session)
                version_no = 0
            else:
                version_no = version_for_subs.version_no + 1
            subtitles = self._subtitles_dict(version_for_subs, version_no)
            return_dict = { "response": "ok",
                            "can_edit" : True,
                            "session_pk" : session.pk,
                            "subtitles" : subtitles }
            if session.base_language:
                return_dict['original_subtitles'] = \
                    self._subtitles_dict(session.base_language.latest_version())
            return return_dict
        else:
            return { 'response': 'cannot_resume' }

    def release_lock(self, request, session_pk):
        language = SubtitlingSession.objects.get(pk=session_pk).language
        if language.can_writelock(request):
            language.release_writelock()
            language.save()
            video_cache.writelocked_langs_clear(language.video.video_id)
        return { "response": "ok" }

    def regain_lock(self, request, session_pk):
        language = SubtitlingSession.objects.get(pk=session_pk).language
        if not language.can_writelock(request):
            return { 'response': 'unlockable' }
        else:
            language.writelock(request)
            language.save()
            video_cache.writelock_add_lang(
                language.video.video_id, language.language)
            return { 'response': 'ok' }


    def finished_subtitles(self, request, session_pk, subtitles=None, 
                           new_title=None, completed=None, 
                           forked=False,
                           throw_exception=False):
        session = SubtitlingSession.objects.get(pk=session_pk)
        if not request.user.is_authenticated():
            return { 'response': 'not_logged_in' }
        if not session.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not session.matches_request(request):
            return { "response" : "does not match request" }

        if throw_exception:
            raise Exception('purposeful exception for testing')

        from apps.teams.moderation import is_moderated, user_can_moderate
        
        language = session.language
        new_version = None
        if subtitles is not None and \
                (len(subtitles) > 0 or language.latest_version(public_only=False) is not None):
            new_version = self._create_version_from_session(session, request.user, forked)
            new_version.save()
            self._save_subtitles(
                new_version.subtitle_set, subtitles, new_version.is_forked)

        language.release_writelock()
        if completed is not None:
            language.is_complete = completed
        if new_title is not None:
            language.title = new_title
        language.save()

        if new_version is not None:
            video_changed_tasks.delay(language.video.id, new_version.id)
        else:
            video_changed_tasks.delay(language.video.id)

        # we have a default user message, since the UI lets users save non
        # changed subs, but the backend will realize and will not save that
        # version. In those cases, we want to show the defatul user message.
        user_message = "Thank you for uploading. It will take a minute or so for your subtitles to appear."
        if new_version is not None and new_version.version_no == 0:
            user_message = "Thank you for uploading. It will take a minute or so for your subtitles to appear."
        elif new_version and is_moderated(new_version):
            
            if user_can_moderate(language.video, request.user) is False:
                user_message = """This video is moderated by %s. 

You will not see your subtitles in our widget when you leave this page, they will only appear on our site. We have saved your work for the team moderator to review. After they approve your subtitles, they will show up on our site and in the widget.
""" % (new_version.video.moderated_by.name)
        return {
            'user_message': user_message,
            'response': 'ok' }

    def _save_subtitles(self, subtitle_set, json_subs, forked):
        for s in json_subs:
            if not forked:
                subtitle_set.create(
                    subtitle_id=s['subtitle_id'],
                    subtitle_text=s['text'])
            else:
                subtitle_set.create(
                    subtitle_id=s['subtitle_id'],
                    subtitle_text=s['text'],
                    start_time=s['start_time'],
                    end_time=s['end_time'],
                    subtitle_order=s['sub_order'])

    def _create_version_from_session(self, session, user=None, forked=False):
        latest_version = session.language.version(public_only=False)
        return models.SubtitleVersion(
            language=session.language,
            version_no=(0 if latest_version is None 
                        else latest_version.version_no + 1),
            is_forked=(session.base_language is None or forked == True),
            datetime_started=session.datetime_started,
            user=user)

    def fetch_subtitles(self, request, video_id, language_pk):
        cache = video_cache.get_subtitles_dict(
            video_id, language_pk, None,
            lambda version: self._subtitles_dict(version))
        return cache

    def get_widget_info(self, request):
        return {
            'all_videos': models.Video.objects.count(),
            'subtitles_fetched_count': models.Video.objects.aggregate(s=Sum('subtitles_fetched_count'))['s'],
            'videos_with_captions': models.Video.objects.exclude(subtitlelanguage=None).count(),
            'translations_count': models.SubtitleLanguage.objects.filter(is_original=False).count()
        }

    def _make_subtitling_session(self, request, language, base_language):
        session = SubtitlingSession(
            language=language,
            base_language=base_language,
            parent_version=language.version(),
            browser_id=request.browser_id)
        if request.user.is_authenticated():
            session.user = request.user
        session.save()
        return session
    
    def _find_base_language(self, base_language):
        if base_language:
            video = base_language.video
            if base_language.is_original or base_language.is_forked:
                return base_language
            else:
                if base_language.standard_language:
                    return base_language.standard_language
                else:
                    return video.subtitle_language()
        else:
            return None

    def _needs_new_sub_language(self, language, base_language):
        if language.standard_language and not base_language:
            # forking existing
            return False
        elif language.is_forked and base_language:
            return True
        else:
            return language.standard_language != base_language 

    def _get_language_for_editing(
        self, request, video_id, language_code, 
        subtitle_language_pk=None, base_language=None):

        video = models.Video.objects.get(video_id=video_id)

        editable = False
        create_new = False

        if subtitle_language_pk is not None:
            language = models.SubtitleLanguage.objects.get(pk=subtitle_language_pk)
            if self._needs_new_sub_language(language, base_language):
                create_new = True
            else:
                editable = language.can_writelock(request)
        else:
            create_new = True
        if create_new:
            standard_language = self._find_base_language(base_language)
            forked = standard_language is None
            language, created = models.SubtitleLanguage.objects.get_or_create(
                video=video,
                language=language_code,
                standard_language=standard_language,
                defaults={
                    'is_forked': forked,
                    'writelock_session_key': '' })
            editable = created or language.can_writelock(request)
        if editable:
            language.writelock(request)
            language.save()
        return language, editable

    def _fix_blank_original(self, video_id):
        # TODO: remove this method as soon as blank SubtitleLanguages
        # become illegal
        video = models.Video.objects.get(video_id=video_id)
        originals = video.subtitlelanguage_set.filter(is_original=True, language='')
        to_delete = []
        if len(originals) > 0:
            for original in originals:
                if not original.latest_version():
                    # result of weird practice of saving SL with is_original=True
                    # and blank language code on Video creation.
                    to_delete.append(original)
                else:
                    # decided to mark authentic blank originals as English.
                    original.language = 'en'
                    original.save()
        for sl in to_delete:
            sl.delete()

    def _save_original_language(self, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        has_original = False
        for sl in video.subtitlelanguage_set.all():
            if sl.is_original and sl.language != language_code:
                sl.is_original = False
                sl.save()
            elif not sl.is_original and sl.language == language_code:
                sl.is_original = True
                sl.save()
            if sl.is_original:
                has_original = True
        if not has_original:
            sl = models.SubtitleLanguage(
                video=video,
                language=language_code,
                is_forked=True,
                is_original=True,
                writelock_session_key='')
            sl.save()

    def _autoplay_subtitles(self, user, video_id, language_pk, version_no):
        cache =  video_cache.get_subtitles_dict(
            video_id, language_pk, version_no, 
            lambda version: self._subtitles_dict(version))
        if cache and cache.get("language", None) is not None:
            cache['language_code'] = cache['language'].language
            cache['language_pk'] = cache['language'].pk
        return cache

    def _subtitles_dict(self, version, forced_version_no=None, force_forked=False):
        language = version.language
        base_language = None
        if language.is_dependent() and not version.is_forked and not force_forked:
            base_language = language.real_standard_language()
        version_no = version.version_no if forced_version_no is None else forced_version_no
        is_latest = False
        latest_version = language.latest_version()
        if latest_version is None or version_no >= latest_version.version_no:
            is_latest = True
        return self._make_subtitles_dict(
            [s.__dict__ for s in version.subtitles()],
            language.language,
            language.pk,
            language.is_original,
            None if base_language is not None else language.is_complete,
            version_no,
            is_latest,
            version.is_forked or force_forked,
            base_language,
            language.get_title())

def language_summary( language):
    summary = {
        'pk': language.pk,
        'language': language.language,
        'dependent': language.is_dependent(),
        'subtitle_count': language.subtitle_count,
        'in_progress': language.is_writelocked }
    if language.is_dependent():
        summary['percent_done'] = language.percent_done
        if language.real_standard_language():
            summary['standard_pk'] = \
                language.real_standard_language().pk
    else:
        summary['is_complete'] = language.is_complete
    return summary
