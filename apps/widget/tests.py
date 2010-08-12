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
from widget import rpc

class RequestMockup(object):
    
    def __init__(self, user):
        self.user = user
        self.session = {}

class TestRpc(TestCase):
    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.user_0 = CustomUser.objects.get(pk=3)
        self.user_1 = CustomUser.objects.get(pk=4)
        self.video_pk = 12
        
    def test_autoplay_subtitles(self):
        request = RequestMockup(self.user_0)
        video = Video.objects.get(pk=self.video_pk)
        subtitles_fetched_count = video.subtitles_fetched_count
        rpc.autoplay_subtitles(request, video, False, None, None)
        video1 = Video.objects.get(pk=self.video_pk)
        self.assertEqual(subtitles_fetched_count+1, video1.subtitles_fetched_count)

    def test_fetch_captions(self):
        request = RequestMockup(self.user_0)
        video = Video.objects.get(pk=self.video_pk)
        subtitles_fetched_count = video.subtitles_fetched_count
        rpc.fetch_captions(request, video.video_id)
        video1 = Video.objects.get(pk=self.video_pk)
        self.assertEqual(subtitles_fetched_count+1, video1.subtitles_fetched_count)

    def test_keep_subtitling_dialog_open(self):
        request = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request, 
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        video_id = return_value['video_id']
        return_value = rpc.start_editing(request, video_id)
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(0, return_value['version'])
        self.assertEqual(0, len(return_value['existing']))
        # the subtitling dialog sends its message back, even 
        # though we've done no subtitling work yet.
        rpc.save_captions(request, video_id, 0, [], [], [])
        video = Video.objects.get(video_id=video_id)
        # if video.captions() returns anything other than None,
        # video.html will show that the video has subtitles.
        self.assertEqual(None, video.captions())

    def test_exit_dialog_then_reopen(self):
        request = RequestMockup(self.user_1)
        return_value = rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        video_id = return_value['video_id']
        rpc.start_editing(request, video_id)
        inserted = [{'caption_id': 'sfdsfsdf',
                     'caption_text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_captions(request, video_id, 0, 
                          [], inserted, [])
        video = Video.objects.get(video_id=video_id)
        self.assertEqual(None, video.captions())
        # now dialog closes and we also wait 30 seconds, so we lose lock.
        rpc.release_video_lock(request, video_id)
        # same user reopens the dialog before anyone else has a chance.
        rpc.show_widget(
            request,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        return_value = rpc.start_editing(request, video_id)
        # make sure we are getting back the unfinished draft.
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(0, return_value['version'])
        self.assertEqual(1, len(return_value['existing']))

    def test_exit_dialog_then_other_user_opens(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'caption_id': 'sfdsfsdf',
                     'caption_text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_captions(request_0, video_id, 0, 
                          [], inserted, [])
        rpc.release_video_lock(request_0, video_id)
        # different user opens the dialog
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are not getting back the unfinished draft.
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(0, return_value['version'])
        self.assertEqual(0, len(return_value['existing']))

    def test_finish_then_other_user_opens(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'caption_id': 'sfdsfsdf',
                     'caption_text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_captions(request_0, video_id, 0, 
                          [], inserted, [])
        rpc.finished_captions(request_0, video_id, 0,
                              [], [], [])
        # different user opens the dialog for video
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are getting back finished subs.
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(1, return_value['version'])
        self.assertEqual(1, len(return_value['existing']))

    def test_finish_then_draft(self):
        request_0 = RequestMockup(self.user_0)
        return_value = rpc.show_widget(
            request_0,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        video_id = return_value['video_id']
        rpc.start_editing(request_0, video_id)
        inserted = [{'caption_id': 'sfdsfsdf',
                     'caption_text': 'hey!',
                     'start_time': 2.3,
                     'end_time': 3.4,
                     'sub_order': 1.0}]
        rpc.save_captions(request_0, video_id, 0, 
                          [], inserted, [])
        rpc.finished_captions(request_0, video_id, 0,
                              [], [], [])
        # user 0 opens dialog again and makes an edit.
        rpc.start_editing(request_0, video_id)
        inserted = [{'caption_id': 'sfdsdsdsdfsdf',
                     'caption_text': 'hey!',
                     'start_time': 3.5,
                     'end_time': 5.4,
                     'sub_order': 2.0}]
        rpc.save_captions(request_0, video_id, 1, [], inserted, [])
        # but, user 0 doesn't finish the new draft and exits the dialog.
        rpc.release_video_lock(request_0, video_id)
        # different user opens the dialog before anyone else has a chance.
        request_1 = RequestMockup(self.user_1)
        rpc.show_widget(
            request_1,
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv', False)
        return_value = rpc.start_editing(request_1, video_id)
        # make sure we are not getting back the draft.
        self.assertEqual(True, return_value['can_edit'])
        self.assertEqual(1, return_value['version'])
        self.assertEqual(1, len(return_value['existing']))
        # the draft VideoCaptionVersion should be deleted at this point.
        self.assertEqual(1, len(Video.objects.get(video_id=video_id).videocaptionversion_set.all()))
