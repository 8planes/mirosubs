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
from widget.rpc import autoplay_subtitles, fetch_captions

class RequestMockup(object):
    
    def __init__(self, user):
        self.user = user

class TestRpc(TestCase):
    fixtures = ['test_widget.json']
    
    def setUp(self):
        self.user = CustomUser.objects.get(pk=3)
        self.video_pk = 12
        
    def test_autoplay_subtitles(self):
        request = RequestMockup(self.user)
        video = Video.objects.get(pk=self.video_pk)
        subtitles_fetched_count = video.subtitles_fetched_count
        autoplay_subtitles(request, video, False, None, None)
        video1 = Video.objects.get(pk=self.video_pk)
        self.failUnlessEqual(subtitles_fetched_count+1, video1.subtitles_fetched_count)

    def test_fetch_captions(self):
        request = RequestMockup(self.user)
        video = Video.objects.get(pk=self.video_pk)
        subtitles_fetched_count = video.subtitles_fetched_count
        fetch_captions(request, video.video_id)
        video1 = Video.objects.get(pk=self.video_pk)
        self.failUnlessEqual(subtitles_fetched_count+1, video1.subtitles_fetched_count)        