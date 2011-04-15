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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
from django.test import TestCase
from videos.models import Video, Action, VIDEO_TYPE_YOUTUBE, UserTestResult, VideoUrl
from apps.auth.models import CustomUser as User
from utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser, YoutubeSubtitleParser, TxtSubtitleParser
from django.core.urlresolvers import reverse
from django.core import mail
from videos.forms import SubtitlesUploadForm
from apps.widget import video_cache
import math_captcha
import os
from django.db.models import ObjectDoesNotExist 
from django.core.management import call_command
from django.core import mail

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

SRT_TEXT_WITH_BLANK = u'''1
00:00:13,34 --> 00:00:24,655
sure I get all the colors
nice-- is equal to 17.

2
00:00:24,655 --> 00:00:27,43

3
00:00:27,43 --> 00:00:29,79
So what's different about this
than what we saw in the last
'''

SRT_TEXT_WITH_TIMECODE_WITHOUT_DECIMAL = u'''1
00:01:01,64 --> 00:01:05,7
this, I guess we could say,
equation or this inequality

2
00:01:05,7 --> 00:01:10
by negative 1, I want to
understand what happens.

3
00:01:10 --> 00:01:18,36
So what's the relation between
negative x and negative 5?

4
00:01:18,36 --> 00:01:21,5
When I say what's the relation,
is it greater than or is
'''


TXT_TEXT = u'''Here is sub 1.

Here is sub 2.

And, sub 3.
'''

class SubtitleParserTest(TestCase):

    def _assert_sub(self, sub, start_time, end_time, sub_text):
        self.assertEqual(sub['start_time'], start_time)
        self.assertEqual(sub['end_time'], end_time)
        self.assertEqual(sub['subtitle_text'], sub_text)
    
    def test_srt(self):
        parser = SrtSubtitleParser(SRT_TEXT)
        result = list(parser)

        self._assert_sub(
            result[0], 0.0, 0.0, 
            u'Don\'t show this text it may be used to insert hidden data')
        self._assert_sub(
            result[1], 1.5, 4.5,
            u'SubRip subtitles capability tester 1.2p by ale5000\nUse Media Player Classic as reference\nThis text should be blue')
        self._assert_sub(
            result[2], 4.5, 4.5,
            u'Hidden')
        self._assert_sub(
            result[3], 7.501, 11.5,
            u'This should be an E with an accent: \xc8\n\u65e5\u672c\u8a9e')
        self._assert_sub(
            result[4], 55.501, 58.5,
            u'Hide these tags: ')

    def test_srt_with_blank(self):
        parser = SrtSubtitleParser(SRT_TEXT_WITH_BLANK)
        result = list(parser)

        self._assert_sub(
            result[0], 13.34, 24.655,
            u'sure I get all the colors\nnice-- is equal to 17.')
        self._assert_sub(
            result[1], 24.655, 27.43,
            u'')
        self._assert_sub(
            result[2], 27.43, 29.79,
            u'So what\'s different about this\nthan what we saw in the last')
    
    def test_srt_with_timecode_without_decimal(self):
        parser = SrtSubtitleParser(SRT_TEXT_WITH_TIMECODE_WITHOUT_DECIMAL)
        result = list(parser)

        self._assert_sub(
            result[0], 61.64, 65.7,
            u'this, I guess we could say,\nequation or this inequality')
        self._assert_sub(
            result[1], 65.7, 70,
            u'by negative 1, I want to\nunderstand what happens.')
        self._assert_sub(
            result[2], 70, 78.36,
            u'So what\'s the relation between\nnegative x and negative 5?')
        self._assert_sub(
            result[3], 78.36, 81.5,
            u'When I say what\'s the relation,\nis it greater than or is')
    
    def test_youtube(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures/youtube_subs_response.json')
        parser = YoutubeSubtitleParser(open(path).read())
        subs = list(parser)
        self.assertAlmostEqual(subs[0]['start_time'], 0.82)
        self.assertAlmostEqual(subs[0]['end_time'], 6.85)

    def test_txt(self):
        parser = TxtSubtitleParser(TXT_TEXT)
        result = list(parser)

        self.assertEqual(3, len(result))

        self.assertEqual(-1, result[0]['start_time'])
        self.assertEqual(-1, result[0]['end_time'])
        self.assertEqual('Here is sub 1.', result[0]['subtitle_text'])

        self.assertEqual(-1, result[1]['start_time'])
        self.assertEqual(-1, result[1]['end_time'])
        self.assertEqual('Here is sub 2.', result[1]['subtitle_text'])
    
class WebUseTest(TestCase):
    def _make_objects(self):
        self.auth = dict(username='admin', password='admin')
        self.user = User.objects.get(username=self.auth['username'])
        self.video = Video.objects.get(video_id='iGzkk7nwWX8F')
        self.video.followers.add(self.user)
        
    def _simple_test(self, url_name, args=None, kwargs=None, status=200, data={}):
        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs), data)
        self.assertEqual(response.status_code, status)
        return response

    def _login(self):
        self.client.login(**self.auth)

class UploadSubtitlesTest(WebUseTest):

    fixtures = ['test.json']

    def _make_data(self, lang='ru', video_pk=None):
        import os
        if video_pk is None:
            video_pk = self.video.id
        return {
            'language': lang,
            'video_language': 'en',
            'video': video_pk,
            'subtitles': open(os.path.join(os.path.dirname(__file__), 'fixtures/test.srt')),
            'is_complete': True
            }

    
    def _make_altered_data(self):
        import os
        return {
            'language': 'ru',
            'video': self.video.id,
            'video_language': 'en',
            'subtitles': open(os.path.join(os.path.dirname(__file__), 'fixtures/test_altered.srt'))
            }

    def setUp(self):
        self._make_objects()
        
    def test_upload_subtitles(self):
        self._simple_test('videos:upload_subtitles', status=302)
        
        self._login()
        
        data = self._make_data()

        language = self.video.subtitle_language(data['language'])
        self.assertEquals(language, None)
        original_language = self.video.subtitle_language()
        self.assertFalse(original_language.language)
        
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(video.is_writelocked)
        original_language = video.subtitle_language()
        self.assertEqual(original_language.language, data['video_language'])        
        
        language = video.subtitle_language(data['language'])
        version = language.latest_version()
        self.assertEqual(len(version.subtitles()), 32)
        self.assertTrue(language.is_forked)
        self.assertTrue(version.is_forked)
        self.assertTrue(language.has_version)
        self.assertTrue(language.had_version)
        self.assertEqual(language.is_complete, data['is_complete'])
        self.assertFalse(video.is_subtitled)
        self.assertFalse(video.was_subtitled)
        self.assertEquals(32, language.subtitle_count)
        
        data = self._make_data()
        data['is_complete'] = not data['is_complete']
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        video = Video.objects.get(pk=self.video.pk)
        language = video.subtitle_language(data['language'])
        self.assertEqual(language.is_complete, data['is_complete'])
        self.assertFalse(video.is_writelocked)
        
    def test_upload_original_subtitles(self):
        self._login()
        data = self._make_data(lang='en')
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(1, video.subtitlelanguage_set.count())
        language = video.subtitle_language()
        self.assertEqual('en', language.language)
        self.assertTrue(language.is_original)
        self.assertTrue(language.has_version)
        self.assertTrue(video.is_subtitled)

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

    def test_upload_altered(self):
        self._login()
        data = self._make_data()
        altered_data = self._make_altered_data()
        language = self.video.subtitle_language(data['language'])
        self.assertEqual(language, None)
        
        self.client.post(reverse('videos:upload_subtitles'), data)
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(1, language.subtitleversion_set.count())
        
        self.client.post(reverse('videos:upload_subtitles'), altered_data)
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(2, language.subtitleversion_set.count())
        version = language.latest_version()
        self.assertTrue(version.time_change > 0)
        self.assertTrue(version.text_change > 0)
        self.assertEquals(version.time_change , 1)
        self.assertEquals(version.text_change , 1)

    def test_upload_over_translated(self):
        # for https://www.pivotaltracker.com/story/show/11804745
        from widget.tests import create_two_sub_dependent_draft, RequestMockup
        request = RequestMockup(User.objects.all()[0])
        draft = create_two_sub_dependent_draft(request)
        video_pk = draft.language.video.pk
        video = Video.objects.get(pk=video_pk)
        original_en = video.subtitlelanguage_set.filter(language='en').all()[0]

        self._login()
        data = self._make_data(lang='en', video_pk=video_pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        video = Video.objects.get(pk=video_pk)
        self.assertEqual(3, video.subtitlelanguage_set.count())


class Html5ParseTest(TestCase):
    def _assert(self, start_url, end_url):
        from videos.models import VIDEO_TYPE_HTML5
        video, created = Video.get_or_create_for_url(start_url)
        vu = video.videourl_set.all()[:1].get()
        self.assertEquals(VIDEO_TYPE_HTML5, vu.type)
        self.assertEquals(end_url, vu.url)

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

    def test_youtube_subs_response(self):
        import os
        from videos.types.youtube import YoutubeVideoType
        import urllib
        
        def urlopen_mockup(url, *args, **kwargs):
            path = os.path.join(os.path.dirname(__file__), 'fixtures/youtube_subs_response.json')
            return open(path)
        
        _urlopen = urllib.urlopen
        urllib.urlopen = urlopen_mockup
        
        vt = YoutubeVideoType('http://www.youtube.com/watch?v=GcjgWov7mTM')
        video, create = Video.get_or_create_for_url('http://www.youtube.com/watch?v=GcjgWov7mTM', vt)
        res = vt._get_subtitles_from_youtube(video)
        if res is None:
            # api might be down or error
            return
            
        video = Video.objects.get(pk=video.pk)
        version = video.version(language_code='en')
        self.assertFalse(version is None)
        self.assertTrue(len(version.subtitles()))
        self.assertEqual(version.subtitles()[0].text, 'I think what is probably the most misunderstood\nconcept in all of science and as we all know')
        subs = version.subtitles()
        subs.sort(key=lambda s: s.start_time)
        for i in range(1, len(subs)):
            self.assertTrue(subs[i].sub_order > subs[i - 1].sub_order)

        urllib.urlopen = _urlopen


    def test_video_cache_busted_on_delete(self):
        start_url = 'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv'
        video, created = Video.get_or_create_for_url(start_url)
        video_url = video.get_video_url()
        video_pk = video.pk
         # 
        cache_id_1 = video_cache.get_video_id(video_url)
        self.assertTrue(cache_id_1)
        video.delete()
        self.assertEqual(Video.objects.filter(pk=video_pk).count() , 0)
        # when cache is not cleared this will return arn 
        cache_id_2 = video_cache.get_video_id(video_url)
        self.assertNotEqual(cache_id_1, cache_id_2)
        # create a new video with the same url, has to have same# key
        video2, created= Video.get_or_create_for_url(start_url)
        video_url = video2.get_video_url()
        cache_id_3 = video_cache.get_video_id(video_url)
        self.assertEqual(cache_id_3, cache_id_2)

class ViewsTest(WebUseTest):
    
    fixtures = ['test.json']
    
    def setUp(self):
        self._make_objects()
        
    def _test_video_url_make_primary(self):
        #TODO: fix this test
        self._login()
        vu = VideoUrl.objects.all()[:1].get()
        self._simple_test("videos:video_url_make_primary", data={'id': vu.id})
    
    def test_site_feedback(self):
        self._simple_test("videos:site_feedback")
        
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
            video = Video.objects.get(videourl__videoid='osexbB_hX4g', videourl__type=VIDEO_TYPE_YOUTUBE)
        except Video.DoesNotExist:
            self.fail()
        
        self.assertEqual(response['Location'], 'http://testserver'+video.video_link())
        
        len_before = Video.objects.count()
        data = {
            'video_url': 'http://www.youtube.com/watch?v=osexbB_hX4g'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len_before, Video.objects.count())
        self.assertEqual(response['Location'], 'http://testserver'+video.video_link())
    
    def test_video_url_create(self):
        self._login()
        v = Video.objects.all()[:1].get()
        
        user = User.objects.exclude(id=self.user.id)[:1].get()
        user.changes_notification = True
        user.is_active = True
        user.save()
        v.followers.add(user)
        
        data = {
            'url': u'http://www.youtube.com/watch?v=po0jY4WvCIc&feature=grec_index',
            'video': v.pk 
        }
        url = reverse('videos:video_url_create')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        try:
            v.videourl_set.get(videoid='po0jY4WvCIc')
        except ObjectDoesNotExist:
            self.fail()
        self.assertEqual(len(mail.outbox), 1)
        
    def test_video_url_remove(self):
        #TODO: write tests
        pass
    
    def test_video(self):
        self.video.title = 'title'
        self.video.save()
        response = self.client.get(self.video.get_absolute_url('en'))
        self.assertEqual(response.status_code, 200)

        self.video.title = ''
        self.video.save()
        response = self.client.get(self.video.get_absolute_url('en'))
        self.assertEqual(response.status_code, 200)
        
    def test_video_list(self):
        self._simple_test('videos:list')
        self._simple_test('videos:list', data={'o': 'languages_count', 'ot': 'desc'})
        
    def test_actions_list(self):
        self._simple_test('videos:actions_list')
        self._simple_test('videos:actions_list', data={'o': 'created', 'ot': 'desc'})

    def test_bliptv_twice(self):
        VIDEO_FILE = 'http://blip.tv/file/get/Kipkay-AirDusterOfficeWeaponry223.m4v'
        from vidscraper.sites import blip
        old_video_file_url = blip.video_file_url
        blip.video_file_url = lambda x: VIDEO_FILE
        Video.get_or_create_for_url('http://blip.tv/file/4395490')
        blip.video_file_url = old_video_file_url
        # this test passes if the following line executes without throwing an error.
        Video.get_or_create_for_url(VIDEO_FILE)
    
    def test_upload_transcription_file(self):
        #TODO: write tests
        pass
    
    def test_legacy_history(self):
        #TODO: write tests
        pass
    
    def test_stop_notification(self):
        #TODO: write tests
        pass
    
    def test_subscribe_to_updates(self):
        #TODO: write test
        pass
    
    def test_paste_transcription(self):
        user1 = User.objects.get(username='admin1')
        self.client.login(username='admin1', password='admin')
        
        self.assertFalse(self.video.followers.filter(pk=user1.pk).exists())
        
        mail.outbox = []
        
        language_code = u"el"

        data = {
            "video": u"1",
            "subtitles": u"""#1

#2""",
            "language": language_code,
            "video_language": u"en"
        }
        language = self.video.subtitle_language(language_code)
        self.assertEquals(language, None)
        response = self.client.post(reverse("videos:paste_transcription"), data)
        self.failUnlessEqual(response.status_code, 200)
        
        language = self.video.subtitle_language(language_code)
        version = language.latest_version()
        self.assertEqual(len(version.subtitles()), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
        self.assertTrue(self.video.followers.filter(pk=user1.pk).exists())
        
    def test_paste_transcription_windows(self):
        self._login()

        language_code = u"el"
        
        data = {
            "video": u"1",
            "subtitles": u"#1\r\n\r\n#2",
            "language": language_code,
            "video_language": u"en"
        }
        response = self.client.post(reverse("videos:paste_transcription"), data)
        language = self.video.subtitle_language(language_code)
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
        
        mail.outbox = []
        data['link'] = 'http://someurl.com'
        self._login()
        response = self.client.post(reverse('videos:email_friend'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
                
    def test_demo(self):
        self._simple_test('videos:demo')
        
    def test_history(self):
        self._simple_test('videos:history', [self.video.video_id])
        self._simple_test('videos:history', [self.video.video_id], data={'o': 'user', 'ot': 'asc'})
        
        sl = self.video.subtitlelanguage_set.all()[:1].get()
        sl.language = 'en'
        sl.save()
        self._simple_test('videos:translation_history', [self.video.video_id, sl.language, sl.id])
        
    def test_revision(self):
        version = self.video.version()
        self._simple_test('videos:revision', [version.id])
        
    def _test_rollback(self):
        #TODO: Seems like roll back is not getting called (on models)
        self._login()
        
        version = self.video.version(0)
        last_version = self.video.version()
        
        self._simple_test('videos:rollback', [version.id], status=302)
        
        new_version = self.video.version()
        self.assertEqual(last_version.version_no+1, new_version.version_no)
    
    def test_model_rollback(self):
        video = Video.objects.all()[:1].get()
        lang = video.subtitlelanguage_set.all()[:1].get()
        v = lang.latest_version()
        v.is_forked = True
        v.save()
        
        new_v = SubtitleVersion(language=lang, version_no=v.version_no+1, datetime_started=datetime.now())
        new_v.save()
        lang = SubtitleLanguage.objects.get(id=lang.id)
        
        self._login()
        
        v.rollback(self.user)
        lang = SubtitleLanguage.objects.get(id=lang.id)
        last_v = lang.latest_version()
        self.assertTrue(last_v.is_forked)
        self.assertFalse(last_v.notification_sent)
        self.assertEqual(last_v.version_no, new_v.version_no+1)
        
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
        self._simple_test('search:index')
        self._simple_test('search:index', data={'o': 'title', 'ot': 'desc'})
    
    def test_counter(self):
        self._simple_test('counter')
    
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
        
    def test_policy_page(self):
        self._simple_test('policy_page')

#Testings VideoType classes
from videos.types.youtube import YoutubeVideoType

class YoutubeVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = YoutubeVideoType
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
    
    def test_create_kwars(self):
        vt = self.vt('http://www.youtube.com/watch?v=woobL2yAxD4')
        kwargs = vt.create_kwars()
        self.assertEqual(kwargs, {'videoid': 'woobL2yAxD4'})
    
    def test_set_values(self):
        youtbe_url = 'http://www.youtube.com/watch?v=_ShmidkrcY0'
        vt = self.vt(youtbe_url)
        
        video, created = Video.get_or_create_for_url(youtbe_url)
        vu = video.videourl_set.all()[:1].get()
        
        self.assertEqual(vu.videoid, '_ShmidkrcY0')
        self.assertTrue(video.title)
        self.assertEqual(video.duration, 79)
        self.assertTrue(video.thumbnail)

    def test_matches_video_url(self):
        for item in self.data:
            self.assertTrue(self.vt.matches_video_url(item['url']))
            self.assertFalse(self.vt.matches_video_url('http://some-other-url.com'))
            self.assertFalse(self.vt.matches_video_url(''))
            self.assertFalse(self.vt.matches_video_url('http://youtube.com/'))
            self.assertFalse(self.vt.matches_video_url('http://youtube.com/some-video/'))
    
    def test_get_video_id(self):
        for item in self.data:
            self.failUnlessEqual(item['video_id'], self.vt._get_video_id(item['url']))
    
from videos.types.htmlfive import HtmlFiveVideoType

class HtmlFiveVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = HtmlFiveVideoType
        
    def test_type(self):
        url = 'http://someurl.com/video.ogv?val=should&val1=be#removed'
        clean_url = 'http://someurl.com/video.ogv'

        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()

        self.assertEqual(vu.url, clean_url)
        self.assertEqual(self.vt.video_url(vu), vu.url)
        
        self.assertTrue(self.vt.matches_video_url(url))
        self.assertTrue(self.vt.matches_video_url('http://someurl.com/video.ogg'))
        self.assertTrue(self.vt.matches_video_url('http://someurl.com/video.mp4'))
        self.assertTrue(self.vt.matches_video_url('http://someurl.com/video.m4v'))
        self.assertTrue(self.vt.matches_video_url('http://someurl.com/video.webm'))
        
        self.assertFalse(self.vt.matches_video_url('http://someurl.ogv'))
        self.assertFalse(self.vt.matches_video_url(''))
        #for this is other type
        self.assertFalse(self.vt.matches_video_url('http://someurl.com/video.flv'))
        self.assertFalse(self.vt.matches_video_url('http://someurl.com/ogv.video'))
        
from videos.types.bliptv import BlipTvVideoType

class BlipTvVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = BlipTvVideoType
        
    def test_type(self):
        url = 'http://blip.tv/file/4297824?utm_source=featured_ep&utm_medium=featured_ep'
        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()
        
        self.assertEqual(vu.videoid, '4297824')
        self.assertTrue(video.title)
        self.assertTrue(video.thumbnail)
        self.assertTrue(vu.url)
        
        self.assertTrue(self.vt.matches_video_url(url))
        self.assertTrue(self.vt.matches_video_url('http://blip.tv/file/4297824'))
        self.assertFalse(self.vt.matches_video_url('http://blip.tv'))
        self.assertFalse(self.vt.matches_video_url(''))
    
    def test_video_title(self):
        url = 'http://blip.tv/file/4914074'
        video, created = Video.get_or_create_for_url(url)
        #really this should be jsut not failed
        self.assertTrue(video.get_absolute_url())
        
from videos.types.dailymotion import DailymotionVideoType
        
class DailymotionVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = DailymotionVideoType
        
    def test_type(self):
        url = 'http://www.dailymotion.com/video/x7u2ww_juliette-drums_lifestyle#hp-b-l'
        vt = self.vt(url)

        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()

        self.assertEqual(vu.videoid, 'x7u2ww')
        self.assertTrue(video.title)
        self.assertTrue(video.thumbnail)
        self.assertEqual(vu.url, 'http://dailymotion.com/video/x7u2ww')
        self.assertTrue(self.vt.video_url(vu))
        
        self.assertTrue(self.vt.matches_video_url(url))
        self.assertFalse(self.vt.matches_video_url(''))
        self.assertFalse(self.vt.matches_video_url('http://www.dailymotion.com'))
        
from videos.types.flv import FLVVideoType

class FLVVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = FLVVideoType
        
    def test_type(self):
        url = 'http://someurl.com/video.flv?val=should&val1=be#removed'
        clean_url = 'http://someurl.com/video.flv'

        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()

        self.assertEqual(vu.url, clean_url)
        self.assertEqual(self.vt.video_url(vu), vu.url)
        
        self.assertTrue(self.vt.matches_video_url(url))
        
        self.assertFalse(self.vt.matches_video_url('http://someurl.flv'))
        self.assertFalse(self.vt.matches_video_url(''))
        self.assertFalse(self.vt.matches_video_url('http://someurl.com/flv.video'))

    def test_blip_type(self):
        url = 'http://blip.tv/file/get/Coldguy-SpineBreakersLiveAWizardOfEarthsea210.FLV'
        video, created = Video.get_or_create_for_url(url)
        video_url = video.videourl_set.all()[0]
        self.assertEqual(self.vt.abbreviation, video_url.type)

from videos.types.vimeo import VimeoVideoType

class VimeoVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = VimeoVideoType
        
    def test_type(self):
        url = 'http://vimeo.com/15786066?some_param=111'

        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()

        self.assertEqual(vu.videoid, '15786066')
        self.assertTrue(self.vt.video_url(vu))
        
        self.assertTrue(self.vt.matches_video_url(url))
        
        self.assertFalse(self.vt.matches_video_url('http://vimeo.com'))
        self.assertFalse(self.vt.matches_video_url(''))
        
from videos.types.base import VideoType, VideoTypeRegistrar
from videos.types import video_type_registrar, VideoTypeError

class VideoTypeRegistrarTest(TestCase):
    
    def test_base(self):
        registrar = VideoTypeRegistrar()
        
        class MockupVideoType(VideoType):
            abbreviation = 'mockup'
            name = 'MockUp'
        
        registrar.register(MockupVideoType)
        self.assertEqual(registrar[MockupVideoType.abbreviation], MockupVideoType)
        self.assertEqual(registrar.choices[-1], (MockupVideoType.abbreviation, MockupVideoType.name))
        
    def test_video_type_for_url(self):
        type = video_type_registrar.video_type_for_url('some url')
        self.assertEqual(type, None)
        type = video_type_registrar.video_type_for_url('http://youtube.com/v=UOtJUmiUZ08')
        self.assertTrue(isinstance(type, YoutubeVideoType))
        self.assertRaises(VideoTypeError, video_type_registrar.video_type_for_url, 'http://youtube.com/v=100500')

class TestFeedsSubmit(TestCase):
    
    def test_video_feed_submit(self):
        old_count = Video.objects.count()
        data = {
            'feed_url': u'http://vimeo.com/channels/beeple/videos/rss'
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertRedirects(response, reverse('videos:create'))
        self.assertNotEqual(old_count, Video.objects.count())

from videos.models import SubtitleLanguage, SubtitleVersion, Subtitle
from datetime import datetime

class TestTasks(TestCase):
    
    fixtures = ['test.json']

    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.language = self.video.subtitle_language()
        self.latest_version = self.language.latest_version()
        
        self.latest_version.user.changes_notification = True
        self.latest_version.user.is_active = True
        self.latest_version.user.save()
        
        self.language.followers.add(self.latest_version.user)
        self.video.followers.add(self.latest_version.user)
        
    def test_send_change_title_email(self):
        from videos.tasks import send_change_title_email
        
        user = User.objects.all()[:1].get()
        
        self.assertFalse(self.video.followers.count() == 1 \
                         and self.video.followers.all()[:1].get() == user)
        
        old_title = self.video.title
        new_title = u'New title'
        self.video.title = new_title
        self.video.save()
        
        result = send_change_title_email.delay(self.video.id, user.id, old_title, new_title)
        if result.failed():
            self.fail(result.traceback)
        self.assertEqual(len(mail.outbox), 1)
        
        #test anonymous editing
        mail.outbox = []
        result = send_change_title_email.delay(self.video.id, None, old_title, new_title)
        if result.failed():
            self.fail(result.traceback)
        self.assertEqual(len(mail.outbox), 1)
        
    def test_notification_sending(self):
        from videos.tasks import send_notification, check_alarm, detect_language
        
        latest_version = self.language.latest_version()
        
        v = SubtitleVersion()
        v.language = self.language
        v.datetime_started = datetime.now()
        v.version_no = latest_version.version_no+1
        v.save()

        for s in latest_version.subtitle_set.all():
            s.duplicate_for(v).save()
        
        s = Subtitle()
        s.version = v
        s.subtitle_id = 'asdasdsadasdasdasd'
        s.subtitle_order = 5
        s.subtitle_text = 'new subtitle'
        s.start_time = 50
        s.end_time = 51
        s.save()        

        v.update_percent_done()
        self.assertEqual(len(mail.outbox), 1)
        
        result = send_notification.delay(v.id)
        if result.failed():
            self.fail(result.traceback)
        
        result = check_alarm.delay(v.id)
        if result.failed():
            self.fail(result.traceback)
        
        result = detect_language.delay(v.id)
        if result.failed():
            self.fail(result.traceback)
        
class TestPercentComplete(TestCase):
    
    fixtures = ['test.json']
    
    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.original_language = self.video.subtitle_language()
        latest_version = self.original_language.latest_version()
        
        translation = SubtitleLanguage()
        translation.video = self.video
        translation.language = 'uk'
        translation.is_original = False
        translation.is_forked = False
        translation.save()

        self.translation = translation
        
        v = SubtitleVersion()
        v.language = translation
        v.version_no = latest_version.version_no+1
        v.datetime_started = datetime.now()
        v.save()
        
        self.translation_version = v
        
        for s in latest_version.subtitle_set.all():
            s.duplicate_for(v).save()
        
    def test_percent_done(self):
        self.translation.update_percent_done()
        self.assertEqual(self.translation.percent_done, 100)
    
    def test_delete_from_original(self):
        latest_version = self.original_language.latest_version()
        latest_version.subtitle_set.all()[:1].get().delete()
        self.translation.update_percent_done()
        self.assertEqual(self.translation.percent_done, 100)
            
    def test_adding_to_original(self):
        latest_version = self.original_language.latest_version()
        s = Subtitle()
        s.version = latest_version
        s.subtitle_id = 'asdasdsadasdasdasd'
        s.subtitle_order = 5
        s.subtitle_text = 'new subtitle'
        s.start_time = 50
        s.end_time = 51
        s.save()
        self.translation.update_percent_done()
        self.assertEqual(self.translation.percent_done, 4/5.*100)
        
    def test_delete_all(self):
        for s in self.translation_version.subtitle_set.all():
            s.delete()

        self.assertEqual(self.translation.percent_done, 0)
    
    def test_delete_from_translation(self):
        self.translation_version.subtitle_set.all()[:1].get().delete()
        self.translation.update_percent_done()
        self.assertEqual(self.translation.percent_done, 75)

    def test_many_subtitles(self):
        latest_version = self.original_language.latest_version()
        for i in range(5, 450):
            s = Subtitle()
            s.version = latest_version
            s.subtitle_id = 'sadfdasf%s' % i
            s.subtitle_order = i
            s.start_time = 50 + i
            s.end_time = 51 + i
            s.save()
            
        self.translation.update_percent_done()
        self.assertEqual(self.translation.percent_done, 0)
    
from videos import alarms
from django.conf import settings

class TestAlert(TestCase):

    fixtures = ['test.json']
    
    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.original_language = self.video.subtitle_language()
        self.latest_version = self.original_language.latest_version()
        settings.ALERT_EMAIL = 'test@test.com'
    
    def _new_version(self, lang=None):
        v = SubtitleVersion()
        v.language = lang or self.original_language
        v.datetime_started = datetime.now()
        lv = v.language.latest_version()
        v.version_no = lv and lv.version_no+1 or 1
        v.save()
        return v       
    
    def test_lose_alert(self):
        v = self._new_version()
        
        s = self.latest_version.subtitle_set.all()[0]
        s.duplicate_for(v).save()
        
        alarms.check_subtitle_version(v)
        
        self.assertEquals(len(mail.outbox), 2)
    
    def test_other_languages_changes(self):
        v = self._new_version()
        l = SubtitleLanguage(video=self.video, language='ru', is_original=False)
        l.save()
        self._new_version(l)
        alarms.check_other_languages_changes(v, ignore_statistic=True)
        self.assertEquals(len(mail.outbox), 1)

    def test_check_language_name_success(self):
        self.original_language.language = 'en'
        self.original_language.save()
        
        v = self._new_version()
        
        Subtitle(version=v, subtitle_id=u'AaAaAaAaAa', subtitle_text='Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.').save()
        Subtitle(version=v, subtitle_id=u'BaBaBaBaBa', subtitle_text='Developed four years ago by a fast-moving online-news operation').save()
        
        alarms.check_language_name(v, ignore_statistic=True)
        
        self.assertEquals(len(mail.outbox), 0)
        
    def test_check_language_name_fail(self):
        self.original_language.language = 'en'
        self.original_language.save()
        
        v = self._new_version()
        
        #this is reliable Ukrainian language
        Subtitle(version=v, subtitle_id=u'AaAaAaAaAa1', subtitle_text=u'Якась не зрозумiла мова.').save()
        Subtitle(version=v, subtitle_id=u'BaBaBaBaBa1', subtitle_text='Якась не зрозумiла мова.').save()
        
        alarms.check_language_name(v, ignore_statistic=True)
        
        self.assertEquals(len(mail.outbox), 1)        
        
        v = self._new_version()
        
        #this one is unreliable
        Subtitle(version=v, subtitle_id=u'AaAaAaAaAa2', subtitle_text=u'Яsdasdзроasdзумiddаsda.').save()
        Subtitle(version=v, subtitle_id=u'BaBaBaBaBa2', subtitle_text='Якasdсьadsdе sdзрdмiлasdва.').save()
        
        alarms.check_language_name(v, ignore_statistic=True)
        
        self.assertEquals(len(mail.outbox), 2)             

class TestModelsSaving(TestCase):
    
    fixtures = ['test.json']
    
    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.language = self.video.subtitle_language()
        self.language.is_complete = False
        self.language.save()
    
    def test_video_languages_count(self):
        #test if fixtures has correct data
        langs_count = self.video.subtitlelanguage_set.filter(had_version=True).count()
        
        self.assertEqual(self.video.languages_count, langs_count)
        self.assertTrue(self.video.languages_count > 0)
        
        self.video.languages_count = 0
        self.video.save()
        self.video.update_languages_count()
        
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count)
        
        self.language.had_version = False
        self.language.save()
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count-1)
        
        self.language.had_version = True
        self.language.save()        
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count)   
        
        self.language.delete()
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count-1)             
        
    def test_subtitle_language_save(self):
        self.assertEqual(self.video.complete_date, None)
        self.assertEqual(self.video.subtitlelanguage_set.count(), 1)

        self.language.is_complete = True
        self.language.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.is_complete = False
        self.language.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)
        
        #add one more SubtitleLanguage
        l = SubtitleLanguage(video=self.video)
        l.is_original = False
        l.is_complete = True
        l.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.is_complete = True
        self.language.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        l.is_complete = False
        l.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.is_complete = False
        self.language.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)

        self.language.is_complete = True
        self.language.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
                
        l.is_complete = True
        l.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.delete()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        l.delete()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)
