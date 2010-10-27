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
from django.test import TestCase
from videos.models import Video, Action, VIDEO_TYPE_YOUTUBE, UserTestResult, StopNotification
from apps.auth.models import CustomUser as User
from videos.utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser
from django.core.urlresolvers import reverse
from django.core import mail
from videos.forms import SubtitlesUploadForm
import math_captcha

math_captcha.forms.math_clean = lambda form: None

SRT_TEXT = u'''1
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

class SubtitleParserTest(TestCase):
    
    def test_srt(self):
        parser = SrtSubtitleParser(SRT_TEXT)
        result = list(parser)
        
        self.assertEqual(result[0]['start_time'], 0.0)
        self.assertEqual(result[0]['end_time'], 0.0)
        self.assertEqual(result[0]['subtitle_text'], u'Don\'t show this text it may be used to insert hidden data')
        
        self.assertEqual(result[1]['start_time'], 1.5)
        self.assertEqual(result[1]['end_time'], 4.5)
        self.assertEqual(result[1]['subtitle_text'], u'SubRip subtitles capability tester 1.2p by ale5000\nUse Media Player Classic as reference\nThis text should be blue')

        self.assertEqual(result[2]['start_time'], 4.5)
        self.assertEqual(result[2]['end_time'], 4.5)
        self.assertEqual(result[2]['subtitle_text'], u'Hidden')
        
        self.assertEqual(result[3]['start_time'], 7.501)
        self.assertEqual(result[3]['end_time'], 11.5)
        self.assertEqual(result[3]['subtitle_text'], u'This should be an E with an accent: \xc8\n\u65e5\u672c\u8a9e')

        self.assertEqual(result[4]['start_time'], 55.501)
        self.assertEqual(result[4]['end_time'], 58.5)
        self.assertEqual(result[4]['subtitle_text'], u'Hide these tags: ')

class WebUseTest(TestCase):
    def _make_objects(self):
        self.auth = dict(username='admin', password='admin')
        self.user = User.objects.get(username=self.auth['username'])
        self.video = Video.objects.get(video_id='iGzkk7nwWX8F')

    def _simple_test(self, url_name, args=None, kwargs=None, status=200, data={}):
        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs), data)
        self.assertEqual(response.status_code, status) 
        return response

    def _login(self):
        self.client.login(**self.auth)

class UploadSubtitlesTest(WebUseTest):

    fixtures = ['test.json']

    def _make_data(self):
        import os
        return {
            'language': 'en',
            'video': self.video.id,
            'subtitles': open(os.path.join(os.path.dirname(__file__), 'fixtures/test.srt'))
            }

    def setUp(self):
        self._make_objects()

    def test_upload_subtitles(self):
        import os.path
        self._simple_test('videos:upload_subtitles', status=302)
        
        self._login()
        
        data = self._make_data()

        language = self.video.subtitle_language(data['language'])
        self.assertEquals(language, None)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        language = self.video.subtitle_language(data['language'])
        version = language.latest_version()
        self.assertEqual(len(version.subtitles()), 32)

    def test_upload_twice(self):
        self._login()
        data = self._make_data()
        self.client.post(reverse('videos:upload_subtitles'), data)
        language = self.video.subtitle_language(data['language'])
        version_no = language.latest_version().version_no
        self.assertEquals(1, language.subtitleversion_set.count())
        # now post the same file.
        data = self._make_data()
        self.client.post(reverse('videos:upload_subtitles'), data)
        self._make_objects()
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(1, language.subtitleversion_set.count())
        self.assertEquals(version_no, language.latest_version().version_no)

class Html5ParseTest(TestCase):
    def _assert(self, start_url, end_url):
        from videos.models import VIDEO_TYPE_HTML5
        video, created = Video.get_or_create_for_url(start_url)
        self.assertEquals(VIDEO_TYPE_HTML5, video.video_type)
        self.assertEquals(end_url, video.video_url)

    def test_ogg(self):
        self._assert(
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
            'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv')

    def test_blip_ogg(self):
        self._assert(
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv',
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv')

    def test_blip_ogg_with_query_string(self):
        self._assert(
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv?bri=1.4&brs=1317',
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv')
        
    def test_mp4(self):
        self._assert(
            'http://videos.mozilla.org/firefox/3.5/switch/switch.mp4',
            'http://videos.mozilla.org/firefox/3.5/switch/switch.mp4')

    def test_blip_mp4_with_file_get(self):
        self._assert(
            'http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles847.mp4',
            'http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles847.mp4')

    def test_blip_mp4_with_query_string(self):
        self._assert(
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.mp4?bri=1.4&brs=1317',
            'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.mp4')

class VideoTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.all()[0]
        self.youtube_video = 'http://www.youtube.com/watch?v=pQ9qX8lcaBQ'
        self.html5_video = 'http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_stereo.ogg'
        
    def test_video_create(self):
        self._create_video(self.youtube_video)
        self._create_video(self.html5_video)
        
    def _create_video(self, video_url):
        video, created = Video.get_or_create_for_url(video_url)
        self.failUnless(video)
        self.failUnless(created)
        more_video, created = Video.get_or_create_for_url(video_url)
        self.failIf(created)
        self.failUnlessEqual(video, more_video)        
    
class ViewsTest(WebUseTest):
    
    fixtures = ['test.json']
    
    def setUp(self):
        self._make_objects()
    
    def test_video_url_make_primary(self):
        self._simple_test("videos:video_url_make_primary")
    
    def test_site_feedback(self):
        self._simple_test("videos:site_feedback")

    def test_api_subtitles(self):
        youtube_id = 'uYT84jZDPE0'
        
        try:
            Video.objects.get(youtube_videoid=youtube_id)
            self.fail()
        except Video.DoesNotExist:
            pass       
        
        url = 'http://www.youtube.com/watch?v=%s' % youtube_id
        self._simple_test("api_subtitles", data={'video_url': url})
        
        try:
            Video.objects.get(youtube_videoid=youtube_id)
        except Video.DoesNotExist:
            self.fail()
    
        self._simple_test("api_subtitles", data={'video_url': url})       
        
        from django.utils import simplejson as json
        
        response = self._simple_test("api_subtitles")
        data = json.loads(response.content)
        self.assertTrue(data['is_error'])
        
    def test_index(self):
        self._simple_test('videos.views.index')
        
    def test_feedback(self):
        data = {
            'email': 'test@test.com',
            'message': 'Test',
            'math_captcha_field': 100500,
            'math_captcha_question': 'test'
        }
        response = self.client.post(reverse('videos:feedback'), data)
        self.assertEqual(response.status_code, 200)
        #self.assertEquals(len(mail.outbox), 2)
    
    def test_ajax_change_video_title(self):
        video = Video.objects.get(video_id='S7HMxzLmS9gw')

        data = {
            'video_id': video.video_id,
            'title': 'New title'
        }
        response = self.client.post(reverse('videos:ajax_change_video_title'), data)
        self.assertEqual(response.status_code, 200)
        
        try:
            Action.objects.get(video=video, \
                               new_video_title=data['title'], \
                               action_type=Action.CHANGE_TITLE)
        except Action.DoesNotExist:
            self.fail()
            
    def test_create(self):
        self._login()
        url = reverse('videos:create')
        
        self._simple_test('videos:create')
        
        data = {
            'video_url': 'http://www.youtube.com/watch?v=osexbB_hX4g&feature=popular'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        try:
            video = Video.objects.get(youtube_videoid='osexbB_hX4g', video_type=VIDEO_TYPE_YOUTUBE)
        except Video.DoesNotExist:
            self.fail()
        
        self.assertEqual(response['Location'], 'http://testserver'+video.get_absolute_url())
        
        len_before = Video.objects.count()    
        data = {
            'video_url': 'http://www.youtube.com/watch?v='+self.video.youtube_videoid
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len_before, Video.objects.count())
        self.assertEqual(response['Location'], 'http://testserver'+self.video.get_absolute_url())
        
    def test_video(self):
        self._simple_test('videos:video', [self.video.video_id])
        
    def test_video_list(self):
        self._simple_test('videos:list')
        self._simple_test('videos:list', data={'o': 'translation_count', 'ot': 'desc'})
        
    def test_actions_list(self):
        self._simple_test('videos:actions_list')
        self._simple_test('videos:actions_list', data={'o': 'created', 'ot': 'desc'})

    def test_paste_transcription(self):
        self._login()
        
        data = {
            "video": u"1",
            "subtitles": u"""#1

#2""",
            "language": u"el"
        }
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(language, None)        
        response = self.client.post(reverse("videos:paste_transcription"), data)
        self.failUnlessEqual(response.status_code, 200)

        language = self.video.subtitle_language(data['language'])
        version = language.latest_version()
        self.assertEqual(len(version.subtitles()), 2)
        
    def test_email_friend(self):
        self._simple_test('videos:email_friend')
        
        data = {
            'from_email': 'test@test.com',
            'to_emails': 'test1@test.com,test@test.com',
            'subject': 'test',
            'message': 'test',
            'math_captcha_field': 100500,
            'math_captcha_question': 'test'            
        }
        response = self.client.post(reverse('videos:email_friend'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)

    def test_demo(self):
        self._simple_test('videos:demo')
        
    def test_history(self):
        self._simple_test('videos:history', [self.video.video_id])
        self._simple_test('videos:history', [self.video.video_id], data={'o': 'user', 'ot': 'asc'})
        
    def test_revision(self):
        version = self.video.version()
        self._simple_test('videos:revision', [version.id])
        
    def test_rollback(self):
        self._login()
        
        version = self.video.version(0)
        last_version = self.video.version()
        
        self._simple_test('videos:rollback', [version.id], status=302)
        
        new_version = self.video.version()
        self.assertEqual(last_version.version_no+1, new_version.version_no)
        
    def test_diffing(self):
        version = self.video.version(0)
        last_version = self.video.version()
        response = self._simple_test('videos:diffing', [version.id, last_version.id])
        self.assertEqual(len(response.context['captions']), 5)
        
    def test_test_form_page(self):
        self._simple_test('videos:test_form_page')
        
        data = {
            'email': 'test@test.ua',
            'task1': 'test1',
            'task2': 'test2',
            'task3': 'test3'
        }
        response = self.client.post(reverse('videos:test_form_page'), data)
        self.assertEqual(response.status_code, 302)
        
        try:
            UserTestResult.objects.get(**data)
        except UserTestResult.DoesNotExist:
            self.fail()
            
    def test_search(self):
        self._simple_test('search')
        self._simple_test('search', data={'o': 'title', 'ot': 'desc'})
    
    def test_counter(self):
        self._simple_test('counter')
        
    def test_stop_notification(self):
        self._login()

        try:
            StopNotification.objects.get(video=self.video, user=self.user).delete()
        except StopNotification.DoesNotExist:
            pass
        
        data = {
            'u': self.user.id,
            'h': self.user.hash_for_video(self.video.video_id)
        }
        response = self.client.get(reverse('videos:stop_notification', args=[self.video.video_id]), data)
        self.assertEqual(response.status_code, 200)
        
        try:
            StopNotification.objects.get(video=self.video, user=self.user)
        except StopNotification.DoesNotExist:
            self.fail()
    
    def test_test_mp4_page(self):
        self._simple_test('test-mp4-page')
        
    def test_test_ogg_page(self):
        self._simple_test('test-ogg-page')
        
    def test_opensubtitles2010_page(self):
        self._simple_test('opensubtitles2010_page')
        
    def test_faq_page(self):
        self._simple_test('faq_page')
        
    def test_about_page(self):
        self._simple_test('about_page')
        
    def test_demo_page(self):
        self._simple_test('demo')
        
    def test_privacy_page(self):
        self._simple_test('privacy_page')
        
    def test_policy_page(self):
        self._simple_test('policy_page')

#Testings VideoType classes
from videos.types.youtube import YoutubeVideoType

class YoutubeModuleTest(TestCase):
    
    def setUp(self):
        self.video_type = YoutubeVideoType()
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
            self.failUnlessEqual(item['video_id'], self.video_type._get_video_id(item['url']))