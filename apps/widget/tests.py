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

from django.test import TestCase
from auth.models import CustomUser
from videos.models import Video, Action
from videos import models
from widget.rpc import Rpc
from widget.null_rpc import NullRpc
from videos.models import VIDEO_SESSION_KEY
from django.core.urlresolvers import reverse
from widget import video_cache

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
        response = self.client.get(reverse('widget:rpc', args=['_maybe_add_video_session']))
        #500, because method does not exists: 500 status
        response = self.client.get(reverse('widget:rpc', args=['undefined_method']))
        #incorect arguments number: 500 status
        response = self.client.get(reverse('widget:rpc', args=['show_widget']))
        print response.status_code

class TestRpc(TestCase):
    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        self.user_1 = CustomUser.objects.get(pk=4)
        self.video_pk = 12
        video_cache.invalidate_video_id(
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv')

    def test_actions_for_subtitle_edit(self):
        request = RequestMockup(self.user_0)
        action_ids = [i.id for i in Action.objects.all()]
        draft = self._create_basic_draft(request, True)
        qs = Action.objects.exclude(id__in=action_ids).exclude(action_type=Action.ADD_VIDEO)
        self.assertEqual(qs.count(), 2)

    def test_no_user_for_video_creation(self):
        request = RequestMockup(self.user_0)
        action_ids = [i.id for i in Action.objects.all()]
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        add_url_action = Action.objects.exclude(id__in=action_ids).exclude(action_type=Action.ADD_VIDEO)[0]
        self.assertEquals(models.Action.ADD_VIDEO_URL, add_url_action.action_type)
        # we can't record the user who opened the widget because of the privacy
        # policy for using the firefox extension.
        self.assertEquals(None, add_url_action.user)

    def test_fetch_subtitles(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        subtitles_fetched_count = draft.video.subtitles_fetched_count
        subs = rpc.fetch_subtitles(request, draft.video.video_id)
        self.assertEqual(1, len(subs['subtitles']))
        video1 = Video.objects.get(pk=draft.video.id)
        self.assertEqual(subtitles_fetched_count + 1, video1.subtitles_fetched_count)

    def test_keep_subtitling_dialog_open(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request, video_id, 'en', 'en')
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))
        # the subtitling dialog sends its message back, even 
        # though we've done no subtitling work yet.
        rpc.save_subtitles(request, return_value['draft_pk'], [])
        video = Video.objects.get(video_id=video_id)
        # if video.latest_version() returns anything other than None,
        # video.html will show that the video has subtitles.
        self.assertEqual(None, video.latest_version())

    def test_exit_dialog_then_reopen(self):
        request = RequestMockup(self.user_1)
        draft = self._create_basic_draft(request)
        self.assertEqual(None, draft.video.latest_version())
        # now dialog closes and we also wait 30 seconds, so we lose lock.
        rpc.release_lock(request, draft.pk)
        # same user reopens the dialog before anyone else has a chance.
        rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request, draft.video.video_id, 'en')
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
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request_0, draft_pk, 
            [_make_packet(inserted=inserted)])
        rpc.release_lock(request_0, draft_pk)
        # different user opens the dialog
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
        # make sure we are not getting back the unfinished draft.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(0, subs['version'])
        self.assertEqual(0, len(subs['subtitles']))

    def test_insert_then_update(self):
        request = RequestMockup(self.user_1)
        draft = self._create_basic_draft(request)
        updated = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey you!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request, draft.pk, 
            [_make_packet(updated=updated)])
        rpc.finished_subtitles(request, draft.pk, [])
        video = Video.objects.get(pk=draft.video.pk)
        self.assertEquals(1, video.subtitle_language().subtitleversion_set.count())

    def test_insert_then_update_same_call(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']

        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        packet_0 = _make_packet(inserted=inserted)
        updated = [{'subtitle_id': 'sfdsfsdf',
                    'text': 'hey you!',
                    'start_time': 2.3,
                    'end_time': 3.4,
                    'sub_order': 1.0}]
        packet_1 = _make_packet(updated=updated, packet_no=2)
        # including both packets in same call, and in reverse order.
        rpc.save_subtitles(request, draft_pk, 
                           [packet_1, packet_0])
        rpc.finished_subtitles(request, draft_pk, [])
        video = Video.objects.get(video_id=video_id)
        self.assertEquals(1, video.subtitle_language().subtitleversion_set.count())
        subs = rpc.fetch_subtitles(request, video_id)
        self.assertEquals('hey you!', subs['subtitles'][0]['text'])

    def test_finish(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request)
        rpc.finished_subtitles(request, draft.pk, [])
        language = Video.objects.get(
            video_id=draft.video.video_id).subtitle_language()
        self.assertTrue(language.was_complete)
        self.assertTrue(language.is_complete)

    def test_change_set(self):
        request = RequestMockup(self.user_0)
        draft = self._create_two_sub_draft(request)
        return_value = rpc.start_editing(request, draft.video.video_id, 'en')
        draft_pk = return_value['draft_pk']
        updated = [{'subtitle_id': 'a',
                     'text': 'hey you!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(updated=updated)])
        rpc.finished_subtitles(request, draft_pk, [])
        video = Video.objects.get(pk=draft.video.pk)
        language = video.subtitle_language()
        self.assertEqual(2, language.subtitleversion_set.count())
        version = language.latest_version()
        self.assertTrue(version.text_change > 0 and version.text_change < 1)
        self.assertTrue(version.time_change == 0)

    def test_cant_edit_because_locked(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id, 'en', 'en')
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
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
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request_0, draft_pk, 
            [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request_0, draft_pk, [])
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

    def test_save_while_not_authenticated(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        response = rpc.save_subtitles(
            request_0, draft_pk,
            [_make_packet(inserted=inserted)])
        self.assertEqual('ok', response['response'])
        response = rpc.finished_subtitles(
            request_0, draft_pk, [])
        self.assertEqual('not_logged_in', response['response'])

    def test_log_in_then_save(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        response = rpc.save_subtitles(
            request_0, draft_pk, 
            [_make_packet(inserted=inserted)])
        self.assertEqual('ok', response['response'])
        request_0.user = self.user_0
        rpc.finished_subtitles(request_0, draft_pk, [])
        self.assertEqual(request_0.user.pk,
                         Video.objects.get(video_id=video_id).\
                             latest_version().user.pk)

    def test_overwrite_anonymous_draft(self):
        request_0 = RequestMockup(NotAuthenticatedUser())
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        rpc.release_lock(request_0, draft_pk)
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
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
        return_value = rpc.start_editing(request_0, video_id, 'en', 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request_0, draft_pk, 
            [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request_0, draft_pk, [])
        # user 0 opens dialog again and makes an edit.
        return_value = rpc.start_editing(request_0, video_id, 'en')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': 'sfdsdsdsdfsdf',
                     'text': 'hey!',
                     'start_time': 3.5,
                     'end_time': 5.4,
                     'sub_order': 2.0}]
        rpc.save_subtitles(
            request_0, draft_pk, 
            [_make_packet(inserted=inserted)])
        # but, user 0 doesn't finish the new draft and exits the dialog.
        rpc.release_lock(request_0, draft_pk)
        # different user opens the dialog before anyone else has a chance.
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, video_id, 'en')
        # make sure we are not getting back the draft.
        self.assertEqual(True, return_value['can_edit'])
        subs = return_value['subtitles']
        self.assertEqual(1, subs['version'])
        self.assertEqual(1, len(subs['subtitles']))

    def test_zero_out_version_1(self):
        request_0 = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request_0, True)
        # now dialog closes and we also wait 30 seconds, so we lose lock.
        rpc.release_lock(request_0, draft.pk)

        # different user opens dialog for video
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, draft.video.video_id, 'en')
        draft_pk = return_value['draft_pk']
        # user_1 updates the solitary caption to have blank text.
        updated = [{'subtitle_id': 'sfdsfsdf',
                     'text': '',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request_1, draft_pk, [_make_packet(updated=updated)])
        rpc.finished_subtitles(request_1, draft_pk, [])
        video = Video.objects.get(pk=draft.video.pk)
        language = video.subtitle_language()
        self.assertEqual(2, language.subtitleversion_set.count())
        self.assertEqual(
            0, language.latest_version().subtitle_set.count())
        self.assertEquals(True, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_zero_out_version_0(self):
        request_0 = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request_0)
        # we update the text of the sole subtitle to be blank.
        updated = [{'subtitle_id': u'sfdsfsdf',
                    'text': '',
                    'start_time': 2.3,
                    'end_time': 3.4,
                    'sub_order': 1.0}]
        rpc.save_subtitles(request_0, draft.pk, 
                           [_make_packet(updated=updated, packet_no=2)])
        rpc.finished_subtitles(
            request_0, draft.pk, [_make_packet()])
        video = Video.objects.get(pk=draft.video.pk)
        language = video.subtitle_language()
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, language.latest_version())
        self.assertEquals(False, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_start_translating(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        # open translation dialog.
        response = rpc.start_editing(request, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(0, subs['version'])
        self.assertEquals(0, len(subs['subtitles']))
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(
            request, draft_pk,
            [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request, draft_pk, [])
        video = models.SubtitleDraft.objects.get(pk=draft_pk).video
        translations = rpc.fetch_subtitles(
            request, video.video_id, language_code='es')
        self.assertEquals(1, len(translations['subtitles']))
        self.assertEquals('heyoes', translations['subtitles'][0]['text'])
        language = video.subtitle_language('es')
        self.assertEquals(1, language.subtitleversion_set.count())

    def test_update_translation(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        # open translation dialog.
        response = rpc.start_editing(request, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(inserted=inserted)])
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': 'new text'}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(updated=updated, packet_no=2)])
        rpc.finished_subtitles(request, draft_pk, [])
        translations = rpc.fetch_subtitles(request, draft.video.video_id, language_code='es')
        self.assertEquals('new text', translations['subtitles'][0]['text'])
        video = models.SubtitleDraft.objects.get(pk=draft_pk).video
        self.assertEquals(1, video.subtitle_language('es').subtitleversion_set.count())

    def test_zero_out_trans_version_1(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_dependent_draft(request, True)
        # user_1 opens translate dialog
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        response = rpc.start_editing(request_1, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        self.assertEquals(True, response['can_edit'])
        subs = response['subtitles']
        self.assertEquals(1, subs['version'])
        self.assertEquals(1, len(subs['subtitles']))
        # user_1 updates solitary translation to have blank text.
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': ''}]
        rpc.save_subtitles(
            request_1, draft_pk, 
            [_make_packet(updated=updated, packet_no=2)])
        rpc.finished_subtitles(request_1, draft_pk, [])
        language = Video.objects.get(pk=draft.video.pk).subtitle_language('es')
        self.assertEquals(2, language.subtitleversion_set.count())
        self.assertEquals(0, language.latest_version().subtitle_set.count())
        self.assertEquals(True, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_zero_out_trans_version_0(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_dependent_draft(request)
        updated = [{'subtitle_id': 'sfdsfsdf', 'text': ''}]
        rpc.save_subtitles(
            request, draft.pk, 
            [_make_packet(updated=updated, packet_no=2)])
        rpc.finished_subtitles(request, draft.pk, [])
        language = Video.objects.get(pk=draft.video.pk).subtitle_language('es')
        self.assertEquals(0, language.subtitleversion_set.count())
        self.assertEquals(None, language.video.latest_version('es'))
        self.assertEquals(False, language.was_complete)
        self.assertEquals(False, language.is_complete)

    def test_edit_existing_original(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        language = models.SubtitleLanguage.objects.get(pk=draft.language.pk)
        # making the language blank to imitate existing vids in system
        language.language = ''
        language.save()
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(
            request, draft.video.video_id, None, None)
        self.assertEquals(1, len(return_value['subtitles']['subtitles']))
        self.assertEquals(False, 'original_subtitles' in return_value)

    def test_fork_then_edit(self):
        request = RequestMockup(self.user_0)
        draft = self._create_two_sub_dependent_draft(request)
        # now fork subtitles
        response = rpc.start_editing(request, draft.video.video_id, 'es', fork=True)
        draft_pk = response['draft_pk']
        updated = [{'subtitle_id': 'a',
                     'text': 'a_esd',
                     'start_time': 2.3,
                     'end_time': 3.2,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request, draft_pk,
            [_make_packet(updated=updated)])
        rpc.finished_subtitles(request, draft_pk, [_make_packet()])
        video = Video.objects.get(pk=draft.video.pk)
        version = video.subtitle_language('es').version()
        self.assertTrue(version.text_change > 0 and version.text_change < 1)
        self.assertTrue(version.time_change > 0 and version.time_change < 1)

    def test_fork(self):
        request = RequestMockup(self.user_0)
        draft = self._create_two_sub_dependent_draft(request)

        language = models.SubtitleLanguage.objects.get(pk=draft.language.pk)
        self.assertEquals(False, language.is_forked)
        self.assertEquals(False, language.latest_version().is_forked)

        # now fork subtitles
        response = rpc.start_editing(request, draft.video.video_id, 'es', fork=True)
        subtitles = response['subtitles']['subtitles']
        self.assertEquals(2, len(subtitles))
        self.assertEquals('a_es', subtitles[0]['text'])
        self.assertEquals(2.3, subtitles[0]['start_time'])
        self.assertEquals(3.4, subtitles[0]['end_time'])
        
        draft_pk = response['draft_pk']
        updated = [{'subtitle_id': subtitles[0]['subtitle_id'],
                     'text': 'a_edited',
                     'start_time': 1.3,
                     'end_time': 3.2,
                     'sub_order': 1.0}]
        rpc.save_subtitles(
            request, draft_pk,
            [_make_packet(updated=updated)])
        rpc.finished_subtitles(request, draft_pk, [_make_packet()])

        language = models.SubtitleLanguage.objects.get(pk=draft.language.pk)
        self.assertEquals(True, language.is_forked)
        self.assertEquals(False, language.version(0).is_forked)
        self.assertEquals(True, language.latest_version().is_forked)

        subs = rpc.fetch_subtitles(request, draft.video.video_id, 'es')
        subtitles = subs['subtitles']
        self.assertEquals(2, len(subtitles))
        self.assertEquals('a_edited', subtitles[0]['text'])
        self.assertEquals(1.3, subtitles[0]['start_time'])
        self.assertEquals(3.2, subtitles[0]['end_time'])
        self.assertEquals(3.4, subtitles[1]['start_time'])
        self.assertEquals(5.8, subtitles[1]['end_time'])

    def test_fork_mid_edit(self):
        request = RequestMockup(self.user_0)
        draft = self._create_two_sub_draft(request)
        response = rpc.start_editing(request, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        inserted = [{'subtitle_id': 'a', 'text': 'a_es'}, 
                    {'subtitle_id': 'b', 'text': 'b_es'}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(inserted=inserted)])
        # now fork.
        response = rpc.fork(request, draft_pk)
        subtitles = response['subtitles']
        self.assertTrue(response['forked'])
        self.assertEquals('es', response['language'])
        self.assertEquals(2, len(subtitles))
        for sub in subtitles:
            self.assertTrue(sub[u'start_time'] > 0)
            self.assertTrue(sub[u'end_time'] > sub['start_time'])

    def test_change_original_language(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        # first claim that the original video language is english
        # and subs are in spanish.
        return_value = rpc.start_editing(request, video_id, 'es', 'en', fork=True)
        draft_pk = return_value['draft_pk']

        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request, draft_pk, 
                           [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request, draft_pk, [])
        rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        # now claim that spanish is the original language
        return_value = rpc.start_editing(request, video_id, 'es', 'es')
        draft_pk = return_value['draft_pk']
        inserted = [{'subtitle_id': u'sddfdsfsdf',
                     'text': 'hey!',
                     'start_time': 3.5,
                     'end_time': 6.4,
                     'sub_order': 2.0}]
        rpc.save_subtitles(
            request, draft_pk,
            [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(
            request, draft_pk, [])
        video = Video.objects.get(video_id=video_id)
        self.assertEquals('es', video.subtitle_language().language)

    def test_insert_duplicate_revision(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        # different user opens dialog for video
        request_1 = RequestMockup(self.user_1, "b")
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        return_value = rpc.start_editing(request_1, draft.video.video_id, 'en')
        draft_pk = return_value['draft_pk']
        # user_1 inserts a new sub, then deletes it
        inserted = [{'subtitle_id': 'abc',
                     'text': '',
                     'start_time': 4.8,
                     'end_time': 9.2,
                     'sub_order': 2.0}]
        rpc.save_subtitles(request_1, draft_pk, [_make_packet(inserted=inserted)])
        rpc.save_subtitles(request_1, draft_pk, [_make_packet(deleted=inserted)])
        rpc.finished_subtitles(request_1, draft_pk, [])
        video = Video.objects.get(pk=draft.video.pk)
        language = video.subtitle_language()
        self.assertEqual(1, language.subtitleversion_set.count())

    def test_only_one_version(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        self.assertEquals(1, draft.video.subtitlelanguage_set.count())

    def test_only_one_video_url(self):
        request = RequestMockup(self.user_0)
        draft = self._create_basic_draft(request, True)
        self.assertEquals(1, draft.video.videourl_set.count())

    def test_only_one_yt_video_url(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request,
            'http://www.youtube.com/watch?v=MJRF8xGzvj4',
            False)
        video = models.Video.objects.get(video_id=return_value['video_id'])
        self.assertEquals(1, video.videourl_set.count())

    def _create_basic_draft(self, request, finished=False):
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False,
            base_state={})
        video_id = return_value['video_id']
        response = rpc.start_editing(
            request, video_id, 'en', 'en',
            base_version_no=None, fork=True)
        draft_pk = response['draft_pk']
        inserted = [{'subtitle_id': u'sfdsfsdf',
                     'text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_subtitles(request, draft_pk, 
                           [_make_packet(inserted=inserted)])
        if finished:
            rpc.finished_subtitles(request, draft_pk, [_make_packet()])
        return models.SubtitleDraft.objects.get(pk=draft_pk)

    def _create_two_sub_draft(self, request):
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            False)
        video_id = return_value['video_id']
        response = rpc.start_editing(request, video_id, 'en', 'en')
        draft_pk = response['draft_pk']
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
        rpc.save_subtitles(request, draft_pk, 
                           [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request, draft_pk, [_make_packet()])
        return models.SubtitleDraft.objects.get(pk=draft_pk)

    def _create_basic_dependent_draft(self, request, finished=False):
        draft = self._create_basic_draft(request, True)
        response = rpc.start_editing(request, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        inserted = [{'subtitle_id': 'sfdsfsdf', 'text': 'heyoes'}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(inserted=inserted)])
        if finished:
            rpc.finished_subtitles(request, draft_pk, [_make_packet()])
        return models.SubtitleDraft.objects.get(pk=draft_pk)

    def _create_two_sub_dependent_draft(self, request):
        draft = self._create_two_sub_draft(request)
        response = rpc.start_editing(request, draft.video.video_id, 'es')
        draft_pk = response['draft_pk']
        inserted = [{'subtitle_id': 'a', 'text': 'a_es'}, 
                    {'subtitle_id': 'b', 'text': 'b_es'}]
        rpc.save_subtitles(
            request, draft_pk, 
            [_make_packet(inserted=inserted)])
        rpc.finished_subtitles(request, draft_pk, [_make_packet()])
        return models.SubtitleDraft.objects.get(pk=draft_pk)

def _make_packet(updated=[], inserted=[], deleted=[], packet_no=1):
    return {
        'packet_no': packet_no,
        'inserted': inserted,
        'deleted': deleted,
        'updated': updated
        }
