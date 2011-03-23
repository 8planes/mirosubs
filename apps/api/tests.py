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
from django.test import TestCase
from videos.models import Video, VIDEO_TYPE_YOUTUBE
from django.core.urlresolvers import reverse
from apps.auth.models import CustomUser as User
from django.utils import simplejson as json

class WebUseTest(TestCase):
    def _make_objects(self):
        self.auth = dict(username='admin', password='admin')
        self.user = User.objects.get(username=self.auth['username'])
        self.video = Video.objects.get(video_key='iGzkk7nwWX8F')

    def _simple_test(self, url_name, args=None, kwargs=None, status=200, data={}):
        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs), data)
        self.assertEqual(response.status_code, status)
        return response

    def _login(self):
        self.client.login(**self.auth)

class ViewsTest(WebUseTest):
    
    fixtures = ['test.json']
    
    def test_subtitles(self):
        youtube_id = 'uYT84jZDPE0'
        
        try:
            Video.objects.get(videourl__videoid=youtube_id, videourl__type=VIDEO_TYPE_YOUTUBE)
            self.fail()
        except Video.DoesNotExist:
            pass
        
        url = 'http://www.youtube.com/watch?v=%s' % youtube_id
        self._simple_test("api:subtitles", data={'video_url': url})
        
        try:
            Video.objects.get(videourl__videoid=youtube_id, videourl__type=VIDEO_TYPE_YOUTUBE)
        except Video.DoesNotExist:
            self.fail()
    
        self._simple_test("api:subtitles", data={'video_url': url})
        
        response = self._simple_test("api:subtitles")
        data = json.loads(response.content)
        self.assertTrue(data['is_error'])

        response = self._simple_test(
            "api:subtitles", 
            data={'video_url': url, 'callback': 'fn'})
        self.assertEquals('fn([]);', response.content)
        self.assertEquals('text/javascript', response['content-type'])
        
    def test_subtitle_existence(self):
        youtube_id = 'uYT84jZDPE0'

        try:
            Video.objects.get(videourl__videoid=youtube_id, videourl__type=VIDEO_TYPE_YOUTUBE)
            self.fail()
        except Video.DoesNotExist:
            pass
        
        url = 'http://www.youtube.com/watch?v=%s' % youtube_id
        response = self._simple_test("api:subtitle_existence", data={'video_url': url})
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        
        try:
            video = Video.objects.get(videourl__videoid=youtube_id, videourl__type=VIDEO_TYPE_YOUTUBE)
        except Video.DoesNotExist:
            self.fail()
            
        video.subtitlelanguage_set.create(language='ru', is_original=False)
        
        url = 'http://www.youtube.com/watch?v=%s' % youtube_id
        response = self._simple_test("api:subtitle_existence", data={'video_url': url})
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        
        response = self._simple_test("api:subtitle_existence")
        data = json.loads(response.content)
        self.assertTrue(data['is_error'])                           