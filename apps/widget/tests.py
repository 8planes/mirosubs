# -*- coding: utf-8 -*-
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

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import os

from django.test import TestCase
from auth.models import CustomUser
from videos.models import Video, Action
from videos import models
from widget.models import SubtitlingSession
from widget.rpc import Rpc
from widget.null_rpc import NullRpc
from django.core.urlresolvers import reverse
from widget import video_cache
from datetime import datetime, timedelta
from django.conf import settings
from sentry.models import Message

class FakeDatetime(object):
    def __init__(self, now):
        self.now_date = now

    def now(self):
        return self.now_date

class RequestMockup(object):
    def __init__(self, user, browser_id="a"):
        self.user = user
        self.session = {}
        self.browser_id = browser_id

class NotAuthenticatedUser:
    def __init__(self):
        self.session = {}
    def is_authenticated(self):
        return False
    def is_anonymous(self):
        return True

rpc = Rpc()
null_rpc = NullRpc()

class TestRpcView(TestCase):
    
    def test_views(self):
        #UnicodeEncodeError: 500 status
        data = {
            'русский': '{}'
        }
        response = self.client.post(reverse('widget:rpc', args=['show_widget']), data)

        #broken json: 500 status
        data = {
            'param': '{broken - json "'
        }
        response = self.client.post(reverse('widget:rpc', args=['show_widget']), data)
        #call private method
        response = self.client.get(reverse('widget:rpc', args=['_subtitle_count']))
        #500, because method does not exists: 500 status
        response = self.client.get(reverse('widget:rpc', args=['undefined_method']))
        #incorect arguments number: 500 status
        response = self.client.get(reverse('widget:rpc', args=['show_widget']))
    
    def test_rpc(self):
        video_url = 'http://www.youtube.com/watch?v=z2U_jf0urVQ'
        video, created = Video.get_or_create_for_url(video_url)
        sl = video.subtitlelanguage_set.all()[:1].get()
        
        url = reverse('widget:rpc', args=['show_widget'])
        data = {
            'is_remote': u'false',
            'base_state': u'{"language_pk":%s,"language_code":""}' % sl.pk,
            'video_url': u'"%s"' % video_url
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
    
class TestRpc(TestCase):
    fixtures = ['test_widget.json', 'test.json']
    
    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        self.user_1 = CustomUser.objects.get(pk=4)
        self.video_pk = 12
        video_cache.invalidate_video_id(
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv')

        

    def test_new_trans_on_fork_creates_new(self):
        # for https://www.pivotaltracker.com/story/show/13248955
        request = RequestMockup(self.user_0)
        session = create_two_sub_dependent_session(request)
        video_pk = session.video.pk
        video = Video.objects.get(pk=video_pk)

        self.client.login(**{"username":"admin", "password":"admin"})
        data = {
            'language': 'en',
            'video_language': 'en',
            'video': video_pk,
            'subtitles': open(os.path.join(settings.PROJECT_ROOT, "apps", "videos", 'fixtures/test.srt')),
            'is_complete': True
            }
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        # now spanish is forked:
        original_spanish = video.subtitlelanguage_set.get(language='es')
        base_language = video.subtitle_language()
        num_langs = video.subtitlelanguage_set.all().count()
        self.assertEqual(2, num_langs)
        self.assertNotEqual(2, len(base_language.latest_subtitles()))

        sub_pk = original_spanish.pk
        return_value = rpc.start_editing(
            request,
            video.video_id, 
            "es", 
            subtitle_language_pk=sub_pk,
            base_language_pk=base_language.pk
        )
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, inserted);

        video = Video.objects.get(pk=video_pk)        
        self.assertEqual(video.subtitlelanguage_set.all().count(), 3)        

        return_value = rpc.start_editing(
            request,
            video.video_id, 
            "es", 
            subtitle_language_pk=sub_pk,
            base_language_pk=base_language.pk
        )

        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, inserted);

        video = Video.objects.get(pk=video_pk)        
        self.assertEqual(video.subtitlelanguage_set.all().count(), 3)

    
    def test_actions_for_subtitle_edit(self):
        request = RequestMockup(self.user_0)
        action_ids = [a.id for a in Action.objects.all()]
        version = self._create_basic_version(request)
        qs = Action.objects.exclude(id__in=action_ids).exclude(action_type=Action.ADD_VIDEO)
        self.assertEqual(qs.count(), 1)

    def test_no_user_for_video_creation(self):
        request = RequestMockup(self.user_0)
        action_ids = [i.id for i in Action.objects.all()]
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)

    def test_fetch_subtitles(self):
        #moved to MySQL in crone
        request = RequestMockup(self.user_0)
        version = self._create_basic_version(request)
        subtitles_fetched_count = version.video.subtitles_fetched_count

        subs = rpc.fetch_subtitles(request, version.video.video_id, version.language.pk)
        self.assertEqual(1, len(subs['subtitles']))
        # can't test counters here because of redis/mysql setup (?)

    def test_add_alternate_urls(self):
        url_0 = 'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv'
        url_1 = 'http://ia700406.us.archive.org/16/items/PeopleOfHtml5-BruceLawsonmp4Version/PeopleOfHtml5-BruceLawson.mp4'
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request, url_0,
            False, additional_video_urls=[url_1])
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, inserted);
        return_value = rpc.show_widget(
            request, url_1,
            False, additional_video_urls=[url_0])
        self.assertEqual(video_id, return_value['video_id'])
        subs = rpc.fetch_subtitles(
            request, video_id, 
            return_value['drop_down_contents'][0]['pk'])
        self.assertEquals(1, len(subs['subtitles']))
        return_value = rpc.show_widget(
            request, url_1, False)
        self.assertEqual(video_id, return_value['video_id'])

    def test_keep_subtitling_dialog_open(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request, video_id, 'en', 
            original_language_code='en')
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))
        # the subtitling dialog pings the server, even 
        # though we've done no subtitling work yet.
        rpc.regain_lock(request, return_value['session_pk'])
        video = Video.objects.get(video_id=video_id)
        # if video.latest_version() returns anything other than None,
        # video.html will show that the video has subtitles.
        self.assertEqual(None, video.latest_version())

    def test_update_after_clearing_session(self):
        request = RequestMockup(self.user_1)
        session = self._start_editing(request)
        # this will fail if locking is dependent on anything in session,
        # which can get cleared after login.
        request.session = {}
        rpc.finished_subtitles(request, session.pk, 
                               [{'subtitle_id': 'aa',
                                 'text': 'hey you!',
                                 'start_time': 2.3,
                                 'end_time': 3.4,
                                 'sub_order': 1.0}])
        video = Video.objects.get(pk=session.video.pk)
        self.assertEquals(1, video.subtitle_language().subtitleversion_set.count())

    def test_finish(self):
        request = RequestMockup(self.user_0)
        version = self._create_basic_version(request)
        language = version.language
        self.assertTrue(language.had_version)
        self.assertTrue(language.has_version)
        self.assertTrue(language.video.is_subtitled)

    def test_get_widget_url(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        language = Video.objects.get(
            video_id=session.video.video_id).subtitle_language()
        # succeeds if no error.

    def test_change_set(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_session(request)
        return_value = rpc.start_editing(
            request, session.video.video_id, 'en')
        session_pk = return_value['session_pk']
        new_subs = [{'subtitle_id': 'a',
                     'text': 'hey you!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0},
                    {'subtitle_id': u'b',
                     'text': 'hey!',
                     'start_time': 3.4,
                     'end_time': 5.8,
                     'sub_order': 2.0}]
        rpc.finished_subtitles(request, session_pk, new_subs)
        video = Video.objects.get(pk=session.video.pk)
        language = video.subtitle_language()
        self.assertEqual(2, language.subtitleversion_set.count())
        version = language.latest_version()
        self.assertTrue(version.text_change > 0 and version.text_change <= 1)
        self.assertEqual(version.time_change, 0)

    def test_cant_edit_because_locked(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
        self.assertEqual(False, return_value['can_edit'])
        self.assertEqual(self.user_0.__unicode__(), 
                         return_value['locked_by'])

    def test_basic(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request_0, session_pk, inserted)
        
        v = models.Video.objects.get(video_id=video_id)

        self.assertEqual(1, v.subtitlelanguage_set.count())
        sl = v.subtitlelanguage_set.all()[0]
        self.assertTrue(sl.is_forked)
        self.assertTrue(sl.is_original)
        self.assertEqual(1, len(sl.latest_version().subtitles()))

    def test_not_complete(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request_0, session_pk, inserted, False)

        v = models.Video.objects.get(video_id=video_id)
        sl = v.subtitle_language('en')
        self.assertFalse(sl.is_complete)

    def test_complete_but_not_synced(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_session(request, completed=True)
        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        self.assertTrue(language.is_complete_and_synced())
        # right now video is complete.
        self.assertTrue(session.video.is_complete)
        completed_langs = session.video.completed_subtitle_languages()
        self.assertEquals(1, len(completed_langs))
        self.assertEquals('en', completed_langs[0].language)

        return_value = rpc.start_editing(
            request, session.video.video_id, 'en',
            subtitle_language_pk=session.language.pk)
        inserted = [{'subtitle_id': 'c',
                     'text': 'unsynced sub',
                     'start_time': -1,
                     'end_time': -1,
                     'sub_order': 3.0}]
        rpc.finished_subtitles(request, return_value['session_pk'], 
                               subtitles=inserted, completed=True)
        video = Video.objects.get(pk=session.language.video.pk)
        language = video.subtitle_language()
        self.assertFalse(language.is_complete_and_synced())
        # since we have one unsynced subtitle, the video is no longer complete.
        self.assertFalse(video.is_complete)
        self.assertEquals(0, len(session.video.completed_subtitle_languages()))

    def test_complete_with_incomplete_translation(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_session(request, completed=True)
        sl_en = session.language
        response = rpc.start_editing(
            request, session.video.video_id, 'es', base_language_pk=sl_en.pk)
        session_pk = response['session_pk']
        # only covering one.
        inserted = [{'subtitle_id': 'a', 'text': 'a_es'}]
        rpc.finished_subtitles(request, session_pk, subtitles=inserted)
        video = Video.objects.get(pk=session.video.pk)
        self.assertTrue(video.is_complete)
        self.assertEquals(1, len(video.completed_subtitle_languages()))
        self.assertEquals(
            'en', video.completed_subtitle_languages()[0].language)

    def test_incomplete_with_complete_translation(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_dependent_session(request)
        # we now have a 100% translation of an incomplete language.
        video = Video.objects.get(pk=session.video.pk)
        self.assertFalse(video.is_complete)
        self.assertEquals(0, len(video.completed_subtitle_languages()))

    def test_finish_then_other_user_opens(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request_0, session_pk, subtitles=inserted)
        # different user opens the dialog for video
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
        # make sure we are getting back finished subs.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(1, subs['version'])
        self.assertEqual(1, len(subs['subtitles']))

    def test_regain_lock_while_not_authenticated(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        response = rpc.regain_lock(request_0, session_pk)
        self.assertEqual('ok', response['response'])
        response = rpc.finished_subtitles(
            request_0, session_pk, subtitles=inserted)
        self.assertEqual('not_logged_in', response['response'])

    def test_log_in_then_save(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(
            request_0, video_id, 'en', original_language_code='en')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': 'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        response = rpc.regain_lock(request_0, session_pk)
        self.assertEqual('ok', response['response'])
        request_0.user = self.user_0
        rpc.finished_subtitles(request_0, session_pk, inserted)
        self.assertEqual(request_0.user.pk,
                         Video.objects.get(video_id=video_id).\
                             latest_version().user.pk)

    def test_zero_out_version_1(self):
        request_0 = RequestMockup(self.user_0)
        version = self._create_basic_version(request_0)

        # different user opens dialog for video
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, version.language.video.video_id, 'en')
        session_pk = return_value['session_pk']
        # user_1 deletes all the subs
        rpc.finished_subtitles(request_1, session_pk, [])
        video = Video.objects.get(pk=version.language.video.pk)
        language = video.subtitle_language()
        self.assertEqual(2, language.subtitleversion_set.count())
        self.assertEqual(
            0, language.latest_version().subtitle_set.count())
        self.assertEquals(True, language.had_version)
        self.assertEquals(False, language.has_version)

    def test_zero_out_version_0(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False,
            base_state={})
        video_id = return_value['video_id']
        # we submit only blank subs.
        response = rpc.start_editing(
            request_0, video_id, 
            'en', original_language_code='en')
        session_pk = response['session_pk']
        rpc.finished_subtitles(
            request_0,
            session_pk,
            subtitles=[])
        video = Video.objects.get(video_id=video_id)
        language = video.subtitle_language()
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, language.latest_version())
        self.assertEquals(False, language.had_version)
        self.assertEquals(False, language.has_version)

    def test_start_translating(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        sl_en = session.language
        # open translation dialog.
        response = rpc.start_editing(
            request, session.video.video_id, 'es', base_language_pk=sl_en.pk)
        session_pk = response['session_pk']
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(0, subs['version'])
        self.assertEquals(0, len(subs['subtitles']))
        inserted = [{'subtitle_id': 'aa', 'text': 'heyoes'}]
        rpc.finished_subtitles(request, session_pk, inserted)
        video = models.Video.objects.get(id=session.video.id)
        translations = rpc.fetch_subtitles(
            request, video.video_id, video.subtitle_language('es').pk)
        self.assertEquals(1, len(translations['subtitles']))
        self.assertEquals('heyoes', translations['subtitles'][0]['text'])
        language = video.subtitle_language('es')
        self.assertEquals(1, language.subtitleversion_set.count())

    def test_zero_out_trans_version_1(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_dependent_version(request)
        en_sl = session.video.subtitle_language('en')
        # user_1 opens translate dialog
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        response = rpc.start_editing(
            request_1, session.video.video_id, 'es', base_language_pk=en_sl.pk)
        session_pk = response['session_pk']
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(1, subs['version'])
        self.assertEquals(1, len(subs['subtitles']))
        # user_1 deletes the subtitles.
        rpc.finished_subtitles(request_1, session_pk, [])
        language = Video.objects.get(pk=session.video.pk).subtitle_language('es')
        self.assertEquals(2, language.subtitleversion_set.count())
        self.assertEquals(0, language.latest_version().subtitle_set.count())
        self.assertEquals(True, language.had_version)
        self.assertEquals(False, language.has_version)

    def test_zero_out_trans_version_0(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        sl = session.language
        response = rpc.start_editing(
            request, sl.video.video_id, 'es', base_language_pk=sl.pk)
        session_pk = response['session_pk']
        rpc.finished_subtitles(request, session_pk, [])
        language = Video.objects.get(pk=session.video.pk).subtitle_language('es')
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, language.video.latest_version('es'))
        self.assertEquals(False, language.had_version)
        self.assertEquals(False, language.has_version)

    def test_edit_existing_original(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        # making the language blank to imitate existing vids in system
        language.language = ''
        language.save()
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(
            request, session.video.video_id, 'en', subtitle_language_pk=language.pk)
        self.assertEquals(1, len(return_value['subtitles']['subtitles']))
        self.assertEquals(False, 'original_subtitles' in return_value)

    def test_finish_twice(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        self.assertEquals(1, language.subtitle_count)
        first_last_version = language.last_version
        response = rpc.start_editing(
            request, session.video.video_id, 'en', subtitle_language_pk=session.language.pk)
        session_pk = response['session_pk']
        new_subs = [response['subtitles']['subtitles'][0],
                    {'subtitle_id': 'cc',
                     'text': 'hey!',
                     'start_time': 5.3,
                     'end_time': 8.4,
                     'sub_order': 5.0}]
        rpc.finished_subtitles(request, session_pk, new_subs)
        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        second_last_version = language.last_version
        self.assertTrue(second_last_version.version_no > first_last_version.version_no)
        self.assertTrue(first_last_version.pk != second_last_version.pk)
        self.assertEquals(2, language.subtitle_count)

    def test_fork_then_edit(self):
        request = RequestMockup(self.user_0)
        video = self._create_two_sub_forked_subs(request)
        version = video.subtitle_language('es').version()
        self.assertTrue(version.text_change > 0 and version.text_change <= 1)
        self.assertTrue(version.time_change > 0 and version.time_change <= 1)

    def test_fork(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_dependent_session(request)

        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        self.assertEquals(False, language.is_forked)
        self.assertEquals(False, language.latest_version().is_forked)

        # now fork subtitles
        response = rpc.start_editing(
            request, session.video.video_id, 'es', 
            subtitle_language_pk=language.pk)
        sub_state = response['subtitles']
        self.assertEquals(True, sub_state['forked'])
        self.assertTrue(
            ('base_language_pk' not in sub_state) or 
            sub_state['base_language_pk'] is None)
        subtitles = sub_state['subtitles']
        self.assertEquals(2, len(subtitles))
        self.assertEquals('a_es', subtitles[0]['text'])
        self.assertEquals(2.3, subtitles[0]['start_time'])
        self.assertEquals(3.4, subtitles[0]['end_time'])
        
        session_pk = response['session_pk']
        new_subs = [{'subtitle_id': subtitles[0]['subtitle_id'],
                     'text': 'a_edited',
                     'start_time': 1.3,
                     'end_time': 3.2,
                     'sub_order': 1.0},
                    subtitles[1]]
        rpc.finished_subtitles(request, session_pk, new_subs)

        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        self.assertEquals(True, language.is_forked)
        self.assertEquals(False, language.version(0).is_forked)
        self.assertEquals(True, language.latest_version().is_forked)

        subs = rpc.fetch_subtitles(request, session.video.video_id, session.language.pk)
        subtitles = subs['subtitles']
        self.assertEquals(2, len(subtitles))
        self.assertEquals('a_edited', subtitles[0]['text'])
        self.assertEquals(1.3, subtitles[0]['start_time'])
        self.assertEquals(3.2, subtitles[0]['end_time'])
        self.assertEquals(3.4, subtitles[1]['start_time'])
        self.assertEquals(5.8, subtitles[1]['end_time'])

    def test_fork_on_finish(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_dependent_session(request)

        language = models.SubtitleLanguage.objects.get(pk=session.language.pk)
        self.assertEquals(False, language.is_forked)
        self.assertEquals(False, language.latest_version().is_forked)

        # open translation dialog
        response = rpc.start_editing(
            request, session.video.video_id, 'es',
            subtitle_language_pk=language.pk,
            base_language_pk=session.video.subtitle_language().pk)
        session_pk = response['session_pk']

        # fork mid-edit
        subtitles = [{'subtitle_id': u'a',
                 'text': 'uno',
                 'start_time': 1.3,
                 'end_time': 2.4,
                 'sub_order': 1.0},
                {'subtitle_id': u'b',
                 'text': 'dos',
                 'start_time': 6.4,
                 'end_time': 8.8,
                 'sub_order': 2.0}]

        # save as forked.
        rpc.finished_subtitles(
            request, 
            session_pk,
            subtitles=subtitles,
            forked=True)

        # assert models are in correct state
        video = models.Video.objects.get(id=session.video.id)
        self.assertEquals(2, video.subtitlelanguage_set.count())
        es = video.subtitle_language('es')
        self.assertEquals(True, es.is_forked)
        self.assertEquals(2, es.subtitleversion_set.count())
        first = es.version(0)
        self.assertEquals(False, first.is_forked)
        self.assertEquals(True, es.latest_version().is_forked)
        subtitles = es.latest_version().subtitles()
        self.assertEquals(1.3, subtitles[0].start_time)
        self.assertEquals(2.4, subtitles[0].end_time)
        self.assertEquals(6.4, subtitles[1].start_time)
        self.assertEquals(8.8, subtitles[1].end_time)        

    def test_change_original_language_legal(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        # first claim that the original video language is english
        # and subs are in spanish.
        return_value = rpc.start_editing(
            request, video_id, 'es', original_language_code='en')
        session_pk = return_value['session_pk']

        inserted = [{'subtitle_id': u'aa',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, inserted)
        rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        # now claim that spanish is the original language
        es_sl = models.Video.objects.get(video_id=video_id).subtitle_language('es')
        return_value = rpc.start_editing(
            request, video_id, 'es', 
            subtitle_language_pk=es_sl.pk,
            original_language_code='es')
        session_pk = return_value['session_pk']
        inserted = [{'subtitle_id': u'sddfdsfsdf',
                     'text': 'hey!',
                     'start_time': 3.5,
                     'end_time': 6.4,
                     'sub_order': 2.0}]
        rpc.finished_subtitles(
            request, session_pk, inserted)
        video = Video.objects.get(video_id=video_id)
        self.assertEquals('es', video.subtitle_language().language)

    def test_only_one_version(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        self.assertEquals(1, session.video.subtitlelanguage_set.count())

    def test_only_one_video_url(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_version(request)
        self.assertEquals(1, session.video.videourl_set.count())

    def test_only_one_yt_video_url(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request,
            'http://www.youtube.com/watch?v=MJRF8xGzvj4',
            False)
        video = models.Video.objects.get(video_id=return_value['video_id'])
        self.assertEquals(1, video.videourl_set.count())

    def test_autoplay_for_non_finished(self):
        request = RequestMockup(self.user_0)
        self._start_editing(request)
        # request widget with English subtitles preloaded. The widget
        # expected null subtitles in response when the language only
        # has a draft.
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False,
            base_state = { 'language': 'en' })
        self.assertEquals(None, return_value['subtitles'])

    def test_ensure_language_locked_on_regain_lock(self):
        request = RequestMockup(self.user_0)        
        session = self._start_editing(request)
        now = datetime.now().replace(microsecond=0) + timedelta(seconds=20)
        models.datetime = FakeDatetime(now)
        response = rpc.regain_lock(request, session.pk)
        video = models.Video.objects.get(pk=session.video.pk)
        language = video.subtitle_language()
        self.assertEquals(now, language.writelock_time)
        models.datetime = datetime

    def test_create_translation_dependent_on_dependent(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_dependent_session(request)
        response = rpc.start_editing(
            request, session.video.video_id, 'fr', 
            base_language_pk=session.language.pk)
        session_pk = response['session_pk']
        orig_subs = response['original_subtitles']['subtitles']
        self.assertEqual(2, len(orig_subs))
        self.assertEqual('a_es', orig_subs[0]['text'])
        inserted = [{'subtitle_id': 'a', 'text':'frenchtext'}]
        rpc.finished_subtitles(request, session_pk, inserted)
        response = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        lang = [r for r in response['drop_down_contents'] if r['language'] == 'fr'][0]
        subs = rpc.fetch_subtitles(request, session.video.video_id, 
                                   lang['pk'])
        subs = subs['subtitles']
        self.assertEqual(1, len(subs))
        self.assertEqual('frenchtext', subs[0]['text'])
        self.assertEqual(2.3, subs[0]['start_time'])
        self.assertEqual(3.4, subs[0]['end_time'])
        video = models.Video.objects.get(id=session.video.id)
        self.assertEqual(50, video.subtitle_language('fr').percent_done)

    def test_create_translation_dependent_on_forked(self):
        request = RequestMockup(self.user_0)
        video = self._create_two_sub_forked_subs(request)

        # create a dependent french translation fr
        response = rpc.start_editing(
            request, video.video_id, 'fr',
            base_language_pk=video.subtitle_language('es').pk)
        session_pk = response['session_pk']

        inserted = [{'subtitle_id': 'a', 'text':'frenchtext'}]

        rpc.finished_subtitles(request, session_pk, inserted)
        translated_lang =  video.subtitlelanguage_set.get(language='fr')
        # french translation should start 50%
        self.assertEqual(translated_lang.percent_done, 50)

        response = rpc.start_editing(
            request, video.video_id, 'es',
            subtitle_language_pk=video.subtitle_language('es').pk)
        session_pk = response['session_pk']

        # add a subtitle to the spanish one
        new_subs = [{'subtitle_id': 'a',
                     'text': 'a_esd',
                     'start_time': 2.3,
                     'end_time': 3.2,
                     'sub_order': 1.0},
                    {'subtitle_id': 'b',
                     'text': 'b_es',
                     'start_time': 3.4,
                     'end_time': 5.8,
                     'sub_order': 2.0},
                    {'subtitle_id': 'e', 
                      'text': 'd_es',
                     'start_time': 4.3,
                     'end_time': 5.2,
                     'sub_order': 1.0}]

        rpc.finished_subtitles(request, session_pk, new_subs)

        # now check that french has 33% complete
        translated_lang = video.subtitlelanguage_set.get(language='fr')
        percent_done = translated_lang.percent_done

        self.assertEqual(percent_done, 33)

    def test_fork_translation_dependent_on_forked(self):
        request = RequestMockup(self.user_0)
        # first create french translation dependent on forked spanish
        self.test_create_translation_dependent_on_forked()
        # now fork french
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        fr_sl = models.Video.objects.get(video_id=video_id).subtitle_language('fr')
        response = rpc.start_editing(
            request, video_id, 'fr', subtitle_language_pk=fr_sl.pk)
        subtitles = response['subtitles']['subtitles']
        self.assertEquals(1, len(subtitles))
        self.assertEquals('frenchtext', subtitles[0]['text'])
        self.assertEquals(2.3, subtitles[0]['start_time'])
        self.assertEquals(3.2, subtitles[0]['end_time'])

        # update the timing on the French sub.
        session_pk = response['session_pk']
        updated = [{'subtitle_id': subtitles[0]['subtitle_id'],
                     'text': 'a_french_edited',
                     'start_time': 2.35,
                     'end_time': 3.2,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, updated)

        french_lang = models.Video.objects.get(video_id=video_id).subtitle_language('fr')
        self.assertEquals(True, french_lang.is_forked)
        self.assertEquals(2.35, french_lang.latest_version().subtitles()[0].start_time)
        
        spanish_lang = models.Video.objects.get(video_id=video_id).subtitle_language('es')
        self.assertEquals(True, spanish_lang.is_forked)
        self.assertEquals(2.3, spanish_lang.latest_version().subtitles()[0].start_time)

    def test_two_subtitle_langs_can_exist(self):
        request = RequestMockup(self.user_0)

        # create es dependent on en
        session = self._create_basic_dependent_version(request)

        # create forked fr translations
        response = rpc.start_editing(
            request, session.video.video_id, 'fr')
        session_pk = response['session_pk']
        inserted = [{'subtitle_id': 'a',
                     'text': 'a_fr',
                     'start_time': 1.3,
                     'end_time': 2.5,
                     'sub_order': 1.0}]
        rpc.finished_subtitles(request, session_pk, inserted)

        sub_langs = models.Video.objects.get(id=session.video.id).subtitlelanguage_set.filter(language='fr')

        # now someone tries to edit es based on fr.
        
        response = rpc.start_editing(
            request, session.video.video_id, 'es', 
            base_language_pk=sub_langs[0].pk)
        session_pk = response['session_pk']
        inserted = [{'subtitle_id': 'a', 'text': 'a_es'}]
        rpc.finished_subtitles(request, session_pk, inserted)

        # now we should have two SubtitleLanguages for es
        sub_langs = models.Video.objects.get(id=session.video.id).subtitlelanguage_set.filter(language='es')
        self.assertEquals(2, sub_langs.count())

    def test_edit_zero_translation(self):
        request = RequestMockup(self.user_0)
        session = create_two_sub_session(request)
        
        # now create empty subs for a language. We can do this by 
        # starting editing but not finishing. Should create a 0% language.
        response = rpc.start_editing(
            request, session.video.video_id, 'es', 
            base_language_pk=session.video.subtitle_language('en').id)
        session_pk = response['session_pk']
        rpc.release_lock(request, session_pk)

        # now edit the language in earnest, calling finished_subtitles afterward.
        video = models.Video.objects.get(id=session.video.id)
        sl_en = video.subtitle_language('en')
        sl_es = video.subtitle_language('es')

        self.assertEquals(0, sl_es.subtitleversion_set.count())

        response = rpc.start_editing(
            request, video.video_id, 'es',
            subtitle_language_pk=sl_es.pk, 
            base_language_pk=sl_en.pk)
        session_pk = response['session_pk']
        inserted = [{'subtitle_id': u'a',
                     'text': 'heyes!'}]
        # test passes if the following command executes without throwing an exception.
        response= rpc.finished_subtitles(
            request, session_pk, 
            inserted)

        sl_es = models.SubtitleLanguage.objects.get(id=sl_es.id)
        self.assertEquals(1, sl_es.subtitleversion_set.count())

    def test_set_title(self):
        request = RequestMockup(self.user_0)
        session = self._create_basic_dependent_version(request)
        en_sl = session.video.subtitle_language('en')

        # user_1 opens translate dialog
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        response = rpc.start_editing(
            request_1, session.video.video_id, 'es', base_language_pk=en_sl.pk)
        session_pk = response['session_pk']
        title = 'new title'
        return_value = rpc.finished_subtitles(request_1, session_pk, new_title=title)
        language = SubtitlingSession.objects.get(id=session_pk).language
        self.assertEquals(title, language.title)

    def test_youtube_ei_failure(self):
        import sentry_logger
        from utils.requestfactory import RequestFactory
        rf = RequestFactory()
        request = rf.get("/")
        
        num_messages = Message.objects.all().count()
        self.assertEquals(0, num_messages)

        rpc.log_youtube_ei_failure(request, "/test-page")
        new_num_messages = Message.objects.all().count()
        self.assertEquals(num_messages + 1, new_num_messages)

    def test_start_editing_null(self):
        request = RequestMockup(self.user_0)
        response = null_rpc.start_editing(request, 'sadfdsf', 'en')
        self.assertEquals(True, response['can_edit'])

    #def test_fetch_request_dialog_contents(self):
        #request = RequestMockup(self.user_0)
        #request.COOKIES = {settings.USER_LANGUAGES_COOKIE_NAME: ['en']}
        #video = Video.objects.get(id=self.video_pk)
        #response = rpc.fetch_request_dialog_contents(request,
                                                     #video.video_id)
        #self.assertEquals(True, response['all_languages'] or False)

    def test_submit_subtitle_request(self):
        request = RequestMockup(self.user_0)
        video_id = Video.objects.get(id=self.video_pk).video_id
        request_langs = ['en', 'hi', 'fr']
        response = rpc.submit_subtitle_request(request, video_id, request_langs, 
                                               True, '')
        self.assertEqual(True, response.get('status'))
        self.assertEqual(len(request_langs), response.get('count'))


    def _create_basic_version(self, request):
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False,
            base_state={})
        video_id = return_value['video_id']
        response = rpc.start_editing(
            request, video_id, 'en', original_language_code='en')
        session_pk = response['session_pk']
        rpc.finished_subtitles(
            request,
            session_pk,
            [{'subtitle_id': u'aa',
              'text': 'hey!',
              'start_time': 2.3,
              'end_time': 3.4,
              'sub_order': 1.0}])
        return SubtitlingSession.objects.get(pk=session_pk).\
            language.version()

    def _start_editing(self, request):
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False,
            base_state={})
        video_id = return_value['video_id']
        response = rpc.start_editing(
            request, video_id, 'en', original_language_code='en')
        return SubtitlingSession.objects.get(id=response['session_pk'])

    def _create_basic_dependent_version(self, request):
        session = self._create_basic_version(request)
        sl = session.language
        response = rpc.start_editing(
            request, sl.video.video_id, 'es', base_language_pk=sl.pk)
        session_pk = response['session_pk']
        inserted = [{'subtitle_id': 'aa', 'text': 'heyoes'}]
        rpc.finished_subtitles(request, session_pk, inserted)
        return SubtitlingSession.objects.get(pk=session_pk)

    def _create_two_sub_forked_subs(self, request):
        session = create_two_sub_dependent_session(request)
        # now fork subtitles
        response = rpc.start_editing(
            request, session.video.video_id, 'es',
            subtitle_language_pk=session.video.subtitle_language('es').pk)
        session_pk = response['session_pk']
        new_subs = [{'subtitle_id': 'a',
                     'text': 'a_esd',
                     'start_time': 2.3,
                     'end_time': 3.2,
                     'sub_order': 1.0},
                    {'subtitle_id': 'b',
                     'text': 'b_es',
                     'start_time': 3.4,
                     'end_time': 5.8,
                     'sub_order': 2.0}]
        rpc.finished_subtitles(request, session_pk, new_subs)
        return Video.objects.get(pk=session.video.pk)

def create_two_sub_session(request, completed=None):
    return_value = rpc.show_widget(
        request,
        'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
        False)
    video_id = return_value['video_id']
    response = rpc.start_editing(request, video_id, 'en', original_language_code='en')
    session_pk = response['session_pk']
    inserted = [{'subtitle_id': u'a',
                 'text': 'hey!',
                 'start_time': 2.3,
                 'end_time': 3.4,
                 'sub_order': 1.0},
                {'subtitle_id': u'b',
                 'text': 'hey!',
                 'start_time': 3.4,
                 'end_time': 5.8,
                 'sub_order': 2.0}]
    rpc.finished_subtitles(request, session_pk, inserted, completed=completed)
    return SubtitlingSession.objects.get(pk=session_pk)

def create_two_sub_dependent_session(request):
    session = create_two_sub_session(request)
    sl_en = session.video.subtitle_language('en')
    response = rpc.start_editing(
        request, session.video.video_id, 
        'es', base_language_pk=sl_en.pk)
    session_pk = response['session_pk']
    inserted = [{'subtitle_id': 'a', 'text': 'a_es'}, 
                {'subtitle_id': 'b', 'text': 'b_es'}]
    rpc.finished_subtitles(
        request, session_pk, 
        inserted)
    return SubtitlingSession.objects.get(pk=session_pk)

def _make_packet(updated=[], inserted=[], deleted=[], packet_no=1):
    return {
        'packet_no': packet_no,
        'inserted': inserted,
        'deleted': deleted,
        'updated': updated
        }

class TestCache(TestCase):

    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        
    def test_get_cache_url_no_exceptions(self):
        e = None
        try:
            video_cache.get_video_urls("bad key")
        except models.Video.DoesNotExist,e:
            pass
        if e is None:
            self.fail("Bad cache key should fail")

    def test_video_id_not_empty_string(self):
        url = "http://videos-cdn.mozilla.net/serv/mozhacks/demos/screencasts/londonproject/screencast.ogv"
        cache_key = video_cache._video_id_key(url)
        video_cache.cache.set(cache_key, "", video_cache.TIMEOUT)
        video_id = video_cache.get_video_id(url)
        self.assertTrue(bool(video_id))

    def test_empty_id_show_widget(self):
        url = "http://videos-cdn.mozilla.net/serv/mozhacks/demos/screencasts/londonproject/screencast.ogv"
        cache_key = video_cache._video_id_key(url)
        video, create = Video.get_or_create_for_url(url)
        video_cache.cache.set(cache_key, "", video_cache.TIMEOUT)
        # we have a bogus url
        video_id = video_cache.get_video_id(url)
        self.assertTrue(bool(video_id))
        try:
            Video.objects.get(video_id=video_id)
        except Video.DoesNotExist:
            self.fail("Should not point to a non existing video")

    def test_cache_delete_valid_chars(self):
        # this tests depends on memcache being available
        try:
            from memcache.Client import MemcachedKeyCharacterError
        except ImportError:
            return
        request = RequestMockup(self.user_0)
        session = create_two_sub_session(request)
        video = session.video
        # make sure we have video on cache
        video_id =  video_cache.get_video_id(video.get_absolute_url(video.get_video_url()))
        self.assertEquals(video_id, video.video_id)
        self.assertTrue(bool(video_id))
        try:
            video_cache.invalidate_cache(video_id)
        except MemcachedKeyCharacterError:
            self.fail("Cache invalidation should not fail")

from widget.srt_subs import TTMLSubtitles, SRTSubtitles, SBVSubtitles, TXTSubtitles, SSASubtitles

class TestSubtitlesGenerator(TestCase):
    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.subtitles = []
        self.subtitles.append({
            'start': 0,
            'end': 1,
            'text': u''
        })
        self.subtitles.append({
            'start': 1,
            'end': 2,
            'text': u'Не аглійські субтитри. Її'                               
        })
        self.subtitles.append({
            'start': 359999.0,
            'end': 359999.0,
            'text': u"Andres Martinez: Right. And I guess\xa0\x1e\x1e\n I'm tempted to cut to what is the answer."
        })        
        
    def test_ttml(self):
        handler = TTMLSubtitles
        h = handler(self.subtitles, self.video)
        self.assertTrue(unicode(h))
    
    def test_one_subtitle(self):
        subtitles = [{
            'text': u'Witam, jestem Fr\xe9d\xe9ric Couchet, General Manager, od kwietnia', 
            'end': 3.1000000000000001, 
            'start': 0.0
        }]
        self.assertTrue(unicode(SRTSubtitles(subtitles, self.video)))
        self.assertTrue(unicode(TTMLSubtitles(subtitles, self.video)))
        self.assertTrue(unicode(SSASubtitles(subtitles, self.video)))
        self.assertTrue(unicode(SBVSubtitles(subtitles, self.video)))
        self.assertTrue(unicode(TXTSubtitles(subtitles, self.video)))

    
