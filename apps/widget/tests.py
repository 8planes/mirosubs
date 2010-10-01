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

from django.test import TestCase
from auth.models import CustomUser
from videos.models import Video
from widget.rpc import Rpc
from widget.null_rpc import NullRpc

class RequestMockup(object):
    
    def __init__(self, user):
        self.user = user
        self.session = {}

class NotAuthenticatedUser:
    def is_authenticated(self):
        return False
    def is_anonymous(self):
        return True

rpc = Rpc()
null_rpc = NullRpc()

class TestNullRpc(TestCase):
    fixtures = ['test_widget.json']

    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        self.user_1 = CustomUser.objects.get(pk=4)

    def test_start_editing_not_logged_in(self):
        request = RequestMockup(NotAuthenticatedUser())
        return_value = null_rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', 
            False)
        video_id = return_value['video_id']
        return_value = null_rpc.start_editing(request, video_id)
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(0, return_value['subtitles']['version'])

    def test_save_subtitles(self):
        request = RequestMockup(self.user_0)
        return_value = null_rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', 
            False)
        video_id = return_value['video_id']
        return_value = null_rpc.start_editing(request, video_id)
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(0, return_value['subtitles']['version'])
        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        return_value = null_rpc.save_subtitles(request, video_id, 
                           [], inserted, [])
        self.assertEquals('ok', return_value['response'])
        null_rpc.finished_subtitles(request, video_id, [], [], [])
        subs = null_rpc.fetch_subtitles(request, video_id)
        self.assertEqual(1, len(subs['subtitles']))
        other_subs = null_rpc.fetch_subtitles(RequestMockup(self.user_1), video_id)
        self.assertEqual(0, len(other_subs['subtitles']))

    def test_translate(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_subtitle(request)
        null_rpc.finished_subtitles(request, video.video_id, [], [], [])
        response = null_rpc.start_editing(request, video.video_id, language_code='es')
        self.assertEquals(True, response['can_edit'])
        inserted = [{'subtitle_id': u'sfdsfsdf', 'text': 'asdfdsf'}]
        null_rpc.save_subtitles(request, video.video_id, [], inserted, [], language_code='es')
        null_rpc.finished_subtitles(request, video.video_id, [], [], [], language_code='es')
        subs = null_rpc.fetch_subtitles(request, video.video_id, language_code='es')
        self.assertEqual(1, len(subs['subtitles']))
        

    def _create_video_with_one_subtitle(self, request):
        return_value = null_rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', 
            False)
        video_id = return_value['video_id']
        null_rpc.start_editing(request, video_id)
        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        null_rpc.save_subtitles(request, video_id, 
                                [], inserted, [])
        return Video.objects.get(video_id=video_id)

class TestRpc(TestCase):
    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        self.user_1 = CustomUser.objects.get(pk=4)
        self.video_pk = 12

    def test_fetch_subtitles(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        subtitles_fetched_count = video.subtitles_fetched_count
        rpc.fetch_subtitles(request, video.video_id)
        video1 = Video.objects.get(pk=video.id)
        self.assertEqual(subtitles_fetched_count + 1, video1.subtitles_fetched_count)

    def test_keep_subtitling_dialog_open(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request, video_id)
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))
        # the subtitling dialog sends its message back, even 
        # though we've done no subtitling work yet.
        rpc.save_subtitles(request, video_id, [], [], [])
        video = Video.objects.get(video_id=video_id)
        # if video.latest_finished_version() returns anything other than None,
        # video.html will show that the video has subtitles.
        self.assertEqual(None, video.latest_finished_version())


    def test_exit_dialog_then_reopen(self):
        request = RequestMockup(self.user_1)
        video = self._create_video_with_one_caption_set(request)
        self.assertEqual(None, video.latest_finished_version())
        # now dialog closes and we also wait 30 seconds, so we lose lock.
        rpc.release_lock(request, video.video_id)
        # same user reopens the dialog before anyone else has a chance.
        rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request, video.video_id)
        # make sure we are getting back the unfinished draft.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(1, len(subs['subtitles']))

    def test_exit_dialog_then_other_user_opens(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request_0, video_id, [], inserted, [])
        rpc.release_lock(request_0, video_id)
        # different user opens the dialog
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are not getting back the unfinished draft.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))

    def test_insert_then_update(self):
        request = RequestMockup(self.user_1)
        video = self._create_video_with_one_caption_set(request)
        updated = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey you!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request, video.video_id, [], [], updated)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        video = Video.objects.get(pk=video.pk)
        self.assertEquals(1, video.subtitle_language().subtitleversion_set.count())

    def test_finish(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        language = Video.objects.get(video_id=video.video_id).subtitle_language()
        self.assertTrue(language.was_complete)
        self.assertTrue(language.is_complete)

    def test_cant_edit_because_locked(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id)
        self.assertEqual(False, return_value['can_edit'])
        self.assertEqual(self.user_0.__unicode__(), 
                         return_value['locked_by'])

    def test_finish_then_other_user_opens(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request_0, video_id, [], inserted, [])
        rpc.finished_subtitles(request_0, video_id, [], [], [])
        # different user opens the dialog for video
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are getting back finished subs.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(1, subs['version'])
        self.assertEqual(1, len(subs['subtitles']))

    def test_save_while_not_authenticated(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        # note: the client-side code of the widget guards 
        # against this behavior.
        response = rpc.save_subtitles(request_0, video_id, [], inserted, [])
        self.assertEqual('not_logged_in', response['response'])

    def test_log_in_then_save(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        request_0.user = self.user_0
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        response = rpc.save_subtitles(request_0, video_id, [], inserted, [])
        self.assertEqual('ok', response['response'])
        rpc.finished_subtitles(request_0, video_id, [], [], [])
        self.assertEqual(request_0.user.pk,
                         Video.objects.get(video_id=video_id).\
                             latest_finished_version().user.pk)

    def test_overwrite_anonymous_draft(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        rpc.release_lock(request_0, video_id)
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id)
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))

    def test_finish_then_draft(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request_0, video_id, [], inserted, [])
        rpc.finished_subtitles(request_0, video_id, [], [], [])
        # user 0 opens dialog again and makes an edit.
        rpc.start_editing(request_0, video_id)
        inserted = [{'subtitle_id': 'sfdsdsdsdfsdf',
                     'text': 'hey!',
                     'start_time': 3.5,
                     'end_time': 5.4,
                     'sub_order': 2.0}]
        rpc.save_subtitles(request_0, video_id, [], inserted, [])
        # but, user 0 doesn't finish the new draft and exits the dialog.
        rpc.release_lock(request_0, video_id)
        # different user opens the dialog before anyone else has a chance.
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are not getting back the draft.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(1, subs['version'])
        self.assertEqual(1, len(subs['subtitles']))

    def test_zero_out_version_1(self):
        request_0 = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request_0)
        rpc.finished_subtitles(request_0, video.video_id, [], [], [])
        # now dialog closes and we also wait 30 seconds, so we lose lock.
        rpc.release_lock(request_0, video.video_id)
        # different user opens dialog for video
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        rpc.start_editing(request_1, video.video_id)
        # user_1 updates the solitary caption to have blank text.
        updated = [{'subtitle_id': 'sfdsfsdf',
                     'text': '',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request_1, video.video_id, [], [], updated)
        rpc.finished_subtitles(request_1, video.video_id, [], [], [])
        video = Video.objects.get(pk=video.pk)
        language = video.subtitle_language()
        self.assertEqual(2, language.subtitleversion_set.count())
        self.assertEqual(
            0, language.latest_finished_version().subtitle_set.count())
        self.assertEquals(True, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_zero_out_version_0(self):
        request_0 = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request_0)
        # we update the text of the sole subtitle to be blank.
        updated = [{'subtitle_id': u'sfdsfsdf',
                    'text': '',
                    'start_time': 2.3,
                    'end_time': 3.4,
                    'sub_order': 1.0}]
        video = Video.objects.get(pk=video.pk)
        rpc.save_subtitles(request_0, video.video_id, [], [], updated)
        rpc.finished_subtitles(request_0, video.video_id, [], [], [])
        language = video.subtitle_language()
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, language.latest_finished_version())
        self.assertEquals(False, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_start_translating(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        rpc.release_lock(request, video.video_id)
        # open translation dialog.
        response = rpc.start_editing(request, video.video_id, language_code='es')
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(0, subs['version'])
        self.assertEquals(0, len(subs['subtitles']))
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(request, video.video_id,
                           [], inserted, [], language_code='es')
        rpc.finished_subtitles(request, video.video_id, [], [], [], language_code='es')
        translations = rpc.fetch_subtitles(
            request, video.video_id, language_code='es')
        self.assertEquals(1, len(translations['subtitles']))
        self.assertEquals('heyoes', translations['subtitles'][0]['text'])
        language = video.subtitle_language('es')
        self.assertEquals(1, language.subtitleversion_set.count())

    def test_update_translation(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_caption_set(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        rpc.release_lock(request, video.video_id)
        # open translation dialog.
        response = rpc.start_editing(request, video.video_id, language_code='es')
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(request, video.video_id, [],
                              inserted, [], language_code='es')
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': 'new text'}]
        rpc.save_subtitles(request, video.video_id, [], [], updated, language_code='es')
        rpc.finished_subtitles(request, video.video_id, [], [], [], language_code='es')
        translations = rpc.fetch_subtitles(request, video.video_id, language_code='es')
        self.assertEquals('new text', translations['subtitles'][0]['text'])
        video = Video.objects.get(pk=video.pk)
        self.assertEquals(1, video.subtitle_language('es').subtitleversion_set.count())

    def test_zero_out_trans_version_1(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_translation(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [], language_code='es')
        # user_1 opens translate dialog
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        response = rpc.start_editing(request_1, video.video_id, language_code='es')
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(1, subs['version'])
        self.assertEquals(1, len(subs['subtitles']))
        # user_1 updates solitary translation to have blank text.
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': ''}]
        rpc.save_subtitles(request_1, video.video_id, [], [], updated, language_code='es')
        rpc.finished_subtitles(request_1, video.video_id, [], [], [], language_code='es')
        language = Video.objects.get(pk=video.pk).subtitle_language('es')
        self.assertEquals(2, language.subtitleversion_set.count())
        self.assertEquals(0, language.latest_finished_version().subtitle_set.count())
        self.assertEquals(True, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_zero_out_trans_version_0(self):
        request = RequestMockup(self.user_0)
        video = self._create_video_with_one_translation(request)
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': ''}]
        rpc.save_subtitles(request, video.video_id, [], [], updated, language_code='es')
        rpc.finished_subtitles(request, video.video_id, [], [], [], language_code='es')
        language = Video.objects.get(pk=video.pk).subtitle_language('es')
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, video.latest_finished_version('es'))
        self.assertEquals(False, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def _create_video_with_one_caption_set(self, request):
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request, video_id)

        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request, video_id, 
                           [], inserted, [])
        return Video.objects.get(video_id=video_id)

    def _create_video_with_one_translation(self, request):
        video = self._create_video_with_one_caption_set(request)
        rpc.finished_subtitles(request, video.video_id, [], [], [])
        rpc.release_lock(request, video.video_id)
        response = rpc.start_editing(request, video.video_id, language_code='es')
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(request, video.video_id, [],
                           inserted, [], language_code='es')
        return video
