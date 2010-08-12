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
from videos.models import Video
from apps.auth.models import CustomUser as User
from youtube import get_video_id
from videos.utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser

class SubtitleParserTest(TestCase):
    
    def test_srt(self):
        text = u'''1
00:00:00,000 --> 00:00:00,000
Don't show this text it may be used to insert hidden data

2
00:00:01,500 --> 00:00:04,500
SubRip subtitles capability tester 1.2p by ale5000
<b><i>Use Media Player Classic as reference</i></b>
<font color="#0000FF">This text should be blue</font>

3
00:00:04,500 --> 00:00:04,500
{\an2}Hidden

4
00:00:07,501 --> 00:00:11,500
This should be an E with an accent: È
日本語

5
00:00:55,501 --> 00:00:58,500
Hide these tags: {\some_letters_or_numbers_or_chars}
'''
        parser = SrtSubtitleParser(text)
        result = list(parser)
        
        self.assertEqual(result[0]['start_time'], 0.0)
        self.assertEqual(result[0]['end_time'], 0.0)
        self.assertEqual(result[0]['caption_text'], u'Don\'t show this text it may be used to insert hidden data')
        
        self.assertEqual(result[1]['start_time'], 1.5)
        self.assertEqual(result[1]['end_time'], 4.5)
        self.assertEqual(result[1]['caption_text'], u'SubRip subtitles capability tester 1.2p by ale5000\nUse Media Player Classic as reference\nThis text should be blue')

        self.assertEqual(result[2]['start_time'], 4.5)
        self.assertEqual(result[2]['end_time'], 4.5)
        self.assertEqual(result[2]['caption_text'], u'Hidden')
        
        self.assertEqual(result[3]['start_time'], 7.501)
        self.assertEqual(result[3]['end_time'], 11.5)
        self.assertEqual(result[3]['caption_text'], u'This should be an E with an accent: \xc8\n\u65e5\u672c\u8a9e')

        self.assertEqual(result[4]['start_time'], 55.501)
        self.assertEqual(result[4]['end_time'], 58.5)
        self.assertEqual(result[4]['caption_text'], u'Hide these tags: ')

        
class YoutubeModuleTest(TestCase):
    
    def setUp(self):
        self.data = [{
            'url': 'http://www.youtube.com/watch#!v=UOtJUmiUZ08&feature=featured&videos=Qf8YDn9mbGs',
            'video_id': 'UOtJUmiUZ08'
        },{
            'url': 'http://www.youtube.com/v/6Z5msRdai-Q',
            'video_id': '6Z5msRdai-Q'
        },{
            'url': 'http://www.youtube.com/watch?v=woobL2yAxD4',
            'video_id': 'woobL2yAxD4'
        },{
            'url': 'http://www.youtube.com/watch?v=woobL2yAxD4&amp;playnext=1&amp;videos=9ikUhlPnCT0&amp;feature=featured',
            'video_id': 'woobL2yAxD4'

        }]
    
    def test_get_video_id(self):
        for item in self.data:
            self.failUnlessEqual(item['video_id'], get_video_id(item['url']))
    
class VideoTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.all()[0]
        self.youtube_video = 'http://www.youtube.com/watch?v=pQ9qX8lcaBQ'
        self.html5_video = 'http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_stereo.ogg'
        
    def test_video_create(self):
        self._create_video(self.youtube_video)
        self._create_video(self.html5_video)
        
    def _create_video(self, video_url):
        video, created = Video.get_or_create_for_url(video_url, self.user)
        self.failUnless(video)
        self.failUnless(created)
        more_video, created = Video.get_or_create_for_url(video_url, self.user)
        self.failIf(created)
        self.failUnlessEqual(video, more_video)        
