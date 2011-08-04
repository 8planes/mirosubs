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

import json

from django.test import TestCase
from videos.models import Video, Action, VIDEO_TYPE_YOUTUBE, UserTestResult, \
    SubtitleLanguage, VideoUrl, VideoFeed
from apps.auth.models import CustomUser as User
from utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser, YoutubeSubtitleParser, TxtSubtitleParser
from django.core.urlresolvers import reverse
from django.core import mail
from videos.forms import SubtitlesUploadForm
from videos.tasks import video_changed_tasks
from apps.videos import metadata_manager
from apps.widget import video_cache
import math_captcha
import os
from django.db.models import ObjectDoesNotExist, Q
from django.core.management import call_command
from django.core import mail
from videos.rpc import VideosApiClass
from widget.tests import RequestMockup

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

    
    def _make_altered_data(self, video=None, language_code='ru', subs_filename='test_altered.srt'):
        import os
        video = video or self.video
        return {
            'language': language_code,
            'video': video.pk,
            'video_language': 'en',
            'subtitles': open(os.path.join(os.path.dirname(__file__), 'fixtures/%s' % subs_filename))
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
        version = language.latest_version(public_only=True)
        self.assertEqual(len(version.subtitles()), 32)
        self.assertTrue(language.is_forked)
        self.assertTrue(version.is_forked)
        self.assertTrue(language.has_version)
        self.assertTrue(language.had_version)
        self.assertEqual(language.is_complete, data['is_complete'])
# FIXME: why should these be false?
#        self.assertFalse(video.is_subtitled)
#        self.assertFalse(video.was_subtitled)
        self.assertEquals(32, language.subtitle_count)
        self.assertEquals(0, language.percent_done)

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
        version_no = language.latest_version(public_only=True).version_no
        self.assertEquals(1, language.subtitleversion_set.count())
        num_languages_1 = self.video.subtitlelanguage_set.all().count()
        # now post the same file.
        data = self._make_data()
        self.client.post(reverse('videos:upload_subtitles'), data)
        self._make_objects()
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(1, language.subtitleversion_set.count())
        self.assertEquals(version_no, language.latest_version(public_only=True).version_no)
        num_languages_2 = self.video.subtitlelanguage_set.all().count()
        self.assertEquals(num_languages_1, num_languages_2)

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
        version = language.latest_version(public_only=True)
        self.assertTrue(version.time_change > 0)
        self.assertTrue(version.text_change > 0)
        self.assertEquals(version.time_change , 1)
        self.assertEquals(version.text_change , 1)

    def test_upload_over_translated(self):
        # for https://www.pivotaltracker.com/story/show/11804745
        from widget.tests import create_two_sub_dependent_session, RequestMockup
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_dependent_session(request)
        video_pk = session.language.video.pk
        video = Video.objects.get(pk=video_pk)
        original_en = video.subtitlelanguage_set.filter(language='en').all()[0]

        self._login()
        data = self._make_data(lang='en', video_pk=video_pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        video = Video.objects.get(pk=video_pk)
        self.assertEqual(2, video.subtitlelanguage_set.count())

    def test_upload_over_empty_translated(self):
        from widget.tests import create_two_sub_session, RequestMockup
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_session(request)
        video_pk = session.language.video.pk
        video = Video.objects.get(pk=video_pk)
        original_en = video.subtitlelanguage_set.filter(language='en').all()[0]

        # save empty espanish
        es = SubtitleLanguage(
            video=video,
            language='ht',
            is_original=False,
            is_forked=False,
            standard_language=original_en)
        es.save()

        # now upload over the original english.
        self._login()
        data = self._make_data(lang='en', video_pk=video_pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

    def test_upload_forks(self):
        from widget.tests import create_two_sub_dependent_session, RequestMockup
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_dependent_session(request)
        video = session.video
        translated = video.subtitlelanguage_set.all().filter(language='es')[0]
        self.assertFalse(translated.is_forked)
        self.assertEquals(False, translated.latest_version(public_only=True).is_forked)

        trans_subs = translated.version().subtitle_set.all()
        
        self._login()
        data = self._make_data(lang='en', video_pk=video.pk)
        translated = video.subtitlelanguage_set.all().filter(language='es')[0]
        trans_subs_before = list(translated.version().subtitle_set.all())
        
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        translated = video.subtitlelanguage_set.all().filter(language='es')[0]
        self.assertTrue(translated.is_forked)
        
        original_subs = video.subtitlelanguage_set.get(language='en').version().subtitle_set.all()
        
        trans_subs_after = translated.version().subtitle_set.all()
        # we want to make sure we did not have a time data
        # but we do now, and text hasn't changed
        for old_sub, new_sub in zip(trans_subs_before, trans_subs_after):
            self.assertEqual(old_sub.subtitle_text, new_sub.subtitle_text)
            self.assertTrue(bool(new_sub.start_time))
            self.assertTrue(bool(new_sub.end_time))
            self.assertTrue(old_sub.start_time is None)
            self.assertTrue(old_sub.end_time is None)
        # now change the translated    
        sub_0= original_subs[1]
        sub_0.start_time = 1.0
        sub_0.save()
        original_subs = video.subtitlelanguage_set.get(language='en').version().subtitle_set.all()
        self.assertNotEqual(sub_0.start_time , original_subs[0].start_time)

    def test_upload_respects_lock(self):
        from widget.tests import create_two_sub_dependent_session, RequestMockup
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_dependent_session(request)
        video = session.video

        self._login()
        translated = video.subtitlelanguage_set.all().filter(language='es')[0]
        translated.writelock(request)
        translated.save()
        data = self._make_data(lang='en', video_pk=video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content[10:-11])
        self.assertFalse(data['success'])


    def test_translations_get_order_after_fork(self):
          # we create en -> es
          # new es has no time data, but does have order
          from widget.tests import create_two_sub_dependent_session, RequestMockup
          request = RequestMockup(User.objects.all()[0])
          session = create_two_sub_dependent_session(request)
          video = session.video
          translated = video.subtitlelanguage_set.all().filter(language='es')[0]
          for sub in translated.version().subtitle_set.all():
              self.assertTrue(sub.start_time is None)
              self.assertTrue(sub.end_time is None)
              self.assertTrue(sub.subtitle_order is None)
          for sub in video.subtitle_language().version().subtitle_set.all():
              self.assertTrue(sub.start_time is not  None)
              self.assertTrue(sub.end_time is not None)
              self.assertTrue(sub.subtitle_order is not None)
          # we upload a new english
          data = self._make_data(lang='en', video_pk=video.pk)
          self._login()

          response = self.client.post(reverse('videos:upload_subtitles'), data)
          self.assertTrue (len(video.version().subtitles()) > len(translated.version().subtitles()))
          self.assertEqual(response.status_code, 200)    
          # now es is forked, which means that it must have timing data AND keep the same ordering from
          translated = video.subtitlelanguage_set.all().filter(language='es')[0]
          self.assertTrue(translated.is_forked)
          translated = video.subtitlelanguage_set.all().filter(language='es')[0]
          subs_trans  = translated.version().subtitle_set.all()
          for sub in subs_trans:
              self.assertTrue(sub.start_time is not None)
              self.assertTrue(sub.end_time is not None)
              self.assertTrue(sub.subtitle_order is not None)
              self.assertTrue(sub.subtitle_id is not None)

    def test_upload_then_rollback_preservs_dependends(self):
        self._login()
        # for https://www.pivotaltracker.com/story/show/14311835
        # 1. Submit a new video.
        video, created = Video.get_or_create_for_url("http://example.com/blah.mp4")
        # 2. Upload some original subs to this video.
        data = self._make_data(lang='en', video_pk=video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        original = video.subtitle_language()
        original_version = version = original.version()
        # 3. Upload another, different file to overwrite the original subs.
        data = self._make_altered_data(language_code='en', video=video, subs_filename="welcome-subs.srt")
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        video = Video.objects.get(pk=video.pk)
        version = video.version()
        self.assertEqual(response.status_code, 200)
        self.assertTrue (len(version.subtitles()) != len(original_version.subtitles()))
        
        # 4. Make a few translations.
        pt = _create_trans(video, latest_version=version, lang_code="pt", forked=False )
        pt_count = len(pt.latest_subtitles())
        # 5. Roll the original subs back to #0. The translations will be wiped clean (to 0 lines).
        original_version.rollback(self.user)
        original_version.save()
        video_changed_tasks.run(original_version.video.id, original_version.id)
        # we should end up with 1 forked pts
        pts = video.subtitlelanguage_set.filter(language='pt')
        self.assertEqual(pts.count(), 1)
        # one which is forkded and must retain the original count
        pt_forked = video.subtitlelanguage_set.get(language='pt', is_forked=True)
        self.assertEqual(len(pt_forked.latest_subtitles()), pt_count)
        # now we roll back  to the second version, we should not be duplicating again
        # because this rollback is already a rollback 
        version.rollback(self.user)
        pts = video.subtitlelanguage_set.filter(language='pt')
        self.assertEqual(pts.count(), 1)
        self.assertEqual(len(pt_forked.latest_subtitles()), pt_count)

    def test_upload_file_with_unsynced(self):
        self._login()
        data = self._make_data()
        data = self._make_altered_data(subs_filename="subs-with-unsynced.srt")
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        language = self.video.subtitlelanguage_set.get(language='ru')
        subs = Subtitle.objects.filter(version=language.version())
        num_subs = len(subs)
        
        num_unsynced = len(Subtitle.objects.unsynced().filter(version=language.version()))

                                       
        self.assertEquals(82, num_subs)
        self.assertEquals(26 ,num_unsynced)

    def test_upload_from_failed_session(self):
        self._login()

        data = self._make_data( video_pk=self.video.pk, lang='ru')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        
        data = self._make_altered_data(video=self.video, language_code='ru', subs_filename='subs-from-fail-session.srt')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        language = self.video.subtitlelanguage_set.get(language='ru')
        subs = Subtitle.objects.filter(version=language.version())

        for sub in subs[8:]:
            self.assertEquals(None, sub.start_time)
            self.assertEquals(None, sub.end_time)

        num_subs = len(subs)
        num_unsynced = len(Subtitle.objects.unsynced().filter(version=language.version()))
        self.assertEquals(10, num_subs)
        self.assertEquals(2 , num_unsynced)
        
    def test_upload_from_widget_last_end_unsynced(self):
        self._login()

        data = self._make_altered_data(video=self.video, language_code='en', subs_filename='subs-last-unsynced.srt')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        language = self.video.subtitle_language('en')
        subs = language.latest_version().subtitles()
        self.assertEquals(7.071, subs[2].start_time)

        from widget.rpc import Rpc
        from widget.tests import RequestMockup, NotAuthenticatedUser
        request = RequestMockup(NotAuthenticatedUser())
        rpc = Rpc()
        subs = rpc.fetch_subtitles(request, self.video.video_id, language.pk)
        last_sub = subs['subtitles'][2]
        self.assertEquals(7.071, last_sub['start_time'])
        self.assertEquals(-1, last_sub['end_time'])        


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

# FIXME: Dmitriy, please fix.
#    def test_video_absolute_url(self):
#        # absolute urls should start with http://
#        # if the urls returned from this method don't start with http,
#        # then the method should be renamed to get_relative_url.
#        self.assertEquals('http', self.video.get_absolute_url()[:4])
        
    def test_video_list(self):
        self._simple_test('videos:list')
        self._simple_test('videos:list', data={'o': 'languages_count', 'ot': 'desc'})

    def test_bliptv_twice(self):
        VIDEO_FILE = 'http://blip.tv/file/get/Kipkay-AirDusterOfficeWeaponry223.m4v'
        from vidscraper.sites import blip
        old_video_file_url = blip.video_file_url
        blip.video_file_url = lambda x: VIDEO_FILE
        Video.get_or_create_for_url('http://blip.tv/file/4395490')
        blip.video_file_url = old_video_file_url
        # this test passes if the following line executes without throwing an error.
        Video.get_or_create_for_url(VIDEO_FILE)
    
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
        version = language.latest_version(public_only=True)
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
        version = language.latest_version(public_only=True)
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
        
        #----------------------------------------
        from videos.share_utils import _make_email_url
        msg = u'Hey-- just found a version of this video ("Tú - Jennifer Lopez") with captions: http://mirosubs.example.com:8000/en/videos/OcuMvG3LrypJ/'
        url = _make_email_url(msg)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
                
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
        last_version = self.video.version(public_only=False)
        
        self._simple_test('videos:rollback', [version.id], status=302)
        
        new_version = self.video.version()
        self.assertEqual(last_version.version_no+1, new_version.version_no)
    
    def test_model_rollback(self):
        video = Video.objects.all()[:1].get()
        lang = video.subtitlelanguage_set.all()[:1].get()
        v = lang.latest_version(public_only=True)
        v.is_forked = True
        v.save()
        
        new_v = SubtitleVersion(language=lang, version_no=v.version_no+1, datetime_started=datetime.now())
        new_v.save()
        lang = SubtitleLanguage.objects.get(id=lang.id)
        
        self._login()
        
        self.client.get(reverse('videos:rollback', args=[v.id]), {})
        lang = SubtitleLanguage.objects.get(id=lang.id)
        last_v = lang.latest_version(public_only=True)
        self.assertTrue(last_v.is_forked)
        self.assertFalse(last_v.notification_sent)
        self.assertEqual(last_v.version_no, new_v.version_no+1)

    def test_rollback_updates_sub_count(self):
        video = Video.objects.all()[:1].get()
        lang = video.subtitlelanguage_set.all()[:1].get()
        v = lang.latest_version(public_only=False)
        num_subs = len(v.subtitles())
        v.is_forked  = True
        v.save()
        new_v = SubtitleVersion(language=lang,
                                version_no=v.version_no+1, datetime_started=datetime.now())
        new_v.save()
        for i in xrange(0,20):
            s, created = Subtitle.objects.get_or_create(
                version=new_v,
                subtitle_id="%s" % i,
                subtitle_order=i,
                subtitle_text="%s lala" % i
            )
        new_version_sub_count = len(new_v.subtitles())
        self._login()
        self.client.get(reverse('videos:rollback', args=[v.id]), {})
        last_v  = SubtitleLanguage.objects.get(id=lang.id).latest_version(public_only=True)
        final_num_subs = len(last_v.subtitles())
        self.assertEqual(final_num_subs, num_subs)

        
    def test_diffing(self):
        version = self.video.version(version_no=0)
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

    def test_volunteer_page(self):
        self._login()
        url = reverse('videos:volunteer_page')
        self._simple_test('videos:volunteer_page')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_volunteer_page_category(self):
        self._login()
        categories = ['featured', 'popular', 'requested', 'latest']
        for category in categories:
            url = reverse('videos:volunteer_category',
                          kwargs={'category': category})
            self._simple_test('videos:volunteer_page')

            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)

class VolunteerRpcTest(TestCase):

    fixtures = ['staging_users.json', 'staging_videos.json',
                'test-userlangs.json']

    def setUp(self):
        from teams.tests import reset_solr
        from utils.translation import get_user_languages_from_request

        self.user = User.objects.all()[0]
        self.request = RequestMockup(self.user)
        self.user_langs = get_user_languages_from_request(self.request)
        reset_solr()
        ## FIXME: Add fixtures which have some subtitles, so that they are included
        ## in the solr index
        ## This should yield a non empty queryset
        #from videos.models import SubtitleLanguage
        #print SubtitleLanguage.objects.filter(subtitle_count__gt=0)


    def test_get_volunteer_sqs(self):

        rpc = VideosApiClass()
        response = rpc._get_volunteer_sqs(self.request, self.user)

        ## A completely analogus db query to the search query
        # TODO: Take into account video_language analogy.
        #db_query = Q(subtitlelanguage__subtitle_count__gt=0) | Q(
            #subtitlelanguage__is_original=True)
        #response_db =  Video.objects.filter(
            #subtitlelanguage__language__in=self.user_langs). \
            #filter(db_query)

        self.assertEqual(1, len(response))

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
        self.shorter_url = "http://youtu.be/HaAVZ2yXDBo"
    
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
            self.assertTrue(self.vt.matches_video_url(self.shorter_url))
    
    def test_get_video_id(self):
        for item in self.data:
            self.failUnlessEqual(item['video_id'], self.vt._get_video_id(item['url']))

    def test_shorter_format(self):
        vt = self.vt(self.shorter_url)
        self.assertTrue(vt)
        self.assertEqual(vt.video_id , self.shorter_url.split("/")[-1])
    
    def test_subtitle_saving(self):
        url = u'http://www.youtube.com/watch?v=63c5p_8hiho'
        
        vt = self.vt(url)
        
        video, created = Video.get_or_create_for_url(url)
        
        langs = video.subtitlelanguage_set.all()
        self.assertEqual(len(langs), 8)
        
        for sl in langs:
            if sl.language:
                subtitles = sl.latest_subtitles()
                self.assertTrue(len(subtitles))
                self.assertTrue(subtitles[5].start_time and subtitles[5].end_time)
    
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
    
    def test_creating(self):
        #this test is for ticket: https://www.pivotaltracker.com/story/show/12996607
        url = 'http://blip.tv/file/5006677/'
        video, created = Video.get_or_create_for_url(url)
        #self.assertTrue(video)
        
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
    
    def test_type1(self):
        from videos.types import VideoTypeError
        url = u'http://www.dailymotion.com/video/edit/xjhzgb_projet-de-maison-des-services-a-fauquembergues_news'
        vt = self.vt(url)
        try:
            vt.get_metadata(vt.videoid)
            self.fail('This link should return wrong response')
        except VideoTypeError:
            pass
        
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
    
    def test1(self):
        #For this video Vimeo API returns response with strance error
        #But we can get data from this response. See vidscraper.sites.vimeo.get_shortmem
        #So if this test is failed - maybe API was just fixed and other response is returned
        url = u'http://vimeo.com/22070806'
        
        video, created = Video.get_or_create_for_url(url)
        
        self.assertNotEqual(video.title, '')
        self.assertNotEqual(video.description, '')
        vu = video.videourl_set.all()[:1].get()

        self.assertEqual(vu.videoid, '22070806')        
        self.assertTrue(self.vt.video_url(vu))
        
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

    def test_inorrect_video_feed_submit(self):
        data = {
            'feed_url': u'http://blip.tv/anyone-but-he/?skin=rss'
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['youtube_form'].errors['feed_url'])

    def test_empty_feed_submit(self):
        import urllib2
        import feedparser
        from StringIO import StringIO
        
        base_open_resource = feedparser._open_resource
        
        def _open_resource_mock(*args, **kwargs):
            return StringIO(str(u"".join([u"<?xml version='1.0' encoding='UTF-8'?>",
            u"<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/'>",
            u"<id>http://gdata.youtube.com/feeds/api/users/test/uploads</id>",
            u"<updated>2011-07-05T09:17:40.888Z</updated>",
            u"<category scheme='http://schemas.google.com/g/2005#kind' term='http://gdata.youtube.com/schemas/2007#video'/>",
            u"<title type='text'>Uploads by test</title>",
            u"<logo>http://www.youtube.com/img/pic_youtubelogo_123x63.gif</logo>",
            u"<link rel='related' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test'/>",
            u"<link rel='alternate' type='text/html' href='https://www.youtube.com/profile_videos?user=test'/>",
            u"<link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads'/>",
            u"<link rel='http://schemas.google.com/g/2005#batch' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads/batch'/>",
            u"<link rel='self' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads?start-index=1&amp;max-results=25'/>",
            u"<author><name>test</name><uri>https://gdata.youtube.com/feeds/api/users/test</uri></author>",
            u"<generator version='2.0' uri='http://gdata.youtube.com/'>YouTube data API</generator>",
            u"<openSearch:totalResults>0</openSearch:totalResults><openSearch:startIndex>1</openSearch:startIndex>",
            u"<openSearch:itemsPerPage>25</openSearch:itemsPerPage></feed>"])))           
        
        feedparser._open_resource = _open_resource_mock

        old_count = Video.objects.count()
        feed_url = u'http://gdata.youtube.com/feeds/api/users/testempty/uploads'
        data = {
            'feed_url': feed_url,
            'save_feed': True
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertRedirects(response, reverse('videos:create'))
        self.assertEqual(old_count, Video.objects.count())
        
        vf = VideoFeed.objects.get(url=feed_url)
        self.assertEqual(vf.last_link, '')
        
        feedparser._open_resource = base_open_resource
        
from apps.videos.types.brigthcove  import BrightcoveVideoType        

class BrightcoveVideoTypeTest(TestCase):
    
    def setUp(self):
        self.vt = BrightcoveVideoType
        
    def test_type(self):
        from apps.videos.models import VIDEO_TYPE_BRIGHTCOVE
        url  = 'http://link.brightcove.com/services/player/bcpid955357260001?bckey=AQ~~,AAAA3ijeRPk~,jc2SmUL6QMyqTwfTFhUbWr3dg6Oi980j&bctid=956115196001'
        video, created = Video.get_or_create_for_url(url)
        vu = video.videourl_set.all()[:1].get()
        self.assertTrue(vu.type ==  VIDEO_TYPE_BRIGHTCOVE == BrightcoveVideoType.abbreviation)
        self.assertTrue(self.vt.video_url(vu))
        self.assertTrue(self.vt.matches_video_url(url))
    
    def test_redirection(self):        
        url  = 'http://bcove.me/7fa5828z'
        vt = video_type_registrar.video_type_for_url(url)
        self.assertTrue(vt)
        self.assertEqual(vt.video_id, '956115196001')        

        
from videos.models import SubtitleLanguage, SubtitleVersion, Subtitle
from datetime import datetime

class TestTasks(TestCase):
    
    fixtures = ['test.json']

    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.language = self.video.subtitle_language()
        self.latest_version = self.language.latest_version(public_only=True)
        
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
        from videos.tasks import video_changed_tasks
        
        latest_version = self.language.latest_version()
        
        v = SubtitleVersion()
        v.language = self.language
        v.datetime_started = datetime.now()
        v.version_no = latest_version.version_no+1
        v.user = User.objects.all()[0]
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

        result = video_changed_tasks.delay(v.video.id, v.id)
        self.assertEqual(len(mail.outbox), 1)

        if result.failed():
            self.fail(result.traceback)
            
        self.assertEqual(len(mail.outbox), 1)

class TestPercentComplete(TestCase):
    
    fixtures = ['test.json']

    def _create_trans(self, latest_version=None, lang_code=None, forked=False):
        translation = SubtitleLanguage()
        translation.video = self.video
        translation.language = lang_code
        translation.is_original = False
        translation.is_forked = forked
        translation.save()

        self.translation = translation
        
        v = SubtitleVersion()
        v.language = translation
        if latest_version:
            v.version_no = latest_version.version_no+1
        else:
            v.version_no = 1
        v.datetime_started = datetime.now()
        v.save()
        
        self.translation_version = v
        if latest_version is not None:
            for s in latest_version.subtitle_set.all():
                s.duplicate_for(v).save()
        return translation
        
    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.original_language = self.video.subtitle_language()
        latest_version = self.original_language.latest_version()
        self.translation = self._create_trans(latest_version, 'uk')
        
    def test_percent_done(self):
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 100)
    
    def test_delete_from_original(self):
        latest_version = self.original_language.latest_version()
        latest_version.subtitle_set.all()[:1].get().delete()
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 100)
            
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

        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 4/5.*100)
        
    def test_delete_all(self):
        for s in self.translation_version.subtitle_set.all():
            s.delete()
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 0)
    
    def test_delete_from_translation(self):
        self.translation_version.subtitle_set.all()[:1].get().delete()
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 75)

    def test_many_subtitles(self):
        latest_version = self.original_language.latest_version()
        for i in range(2, 450):
            s = Subtitle()
            s.version = latest_version
            s.subtitle_id = 'sadfdasf%s' % i
            s.subtitle_order = i
            s.start_time = 50 + i
            s.end_time = 51 + i
            s.subtitle_text = "what %i" % i
            s.save()

        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        # 1% reflects https://www.pivotaltracker.com/story/show/16013319
        self.assertEqual(translation.percent_done, 1)

    def test_count_as_complete(self):
        self.assertFalse(self.video.complete_date)
        # set the original lang as complete, should be completed
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.translation.video.id)
        translation = SubtitleLanguage.objects.get(id=self.translation.id)
        self.assertEqual(translation.percent_done, 100)
        self.assertTrue(translation.is_complete)
        self.translation.save()

#    def test_video_complete_forked_complete(self):                                      
#        self.original_language = self.video.subtitle_language()
#        latest_version = self.original_language.latest_version()
#        new_lang = self._create_trans(latest_version, 'pt', True)
#        self.assertFalse(self.video.is_complete)
# FIXME: this is not complete because the complete language
# has no subtitles.
#        new_lang.is_complete = True             
#        new_lang.save()
#        metadata_manager.update_metadata(self.video.pk)
#        self.assertTrue(self.video.is_complete)
                                               
    def test_video_0_subs_are_never_complete(self):                                      
        self.original_language = self.video.subtitle_language()
        new_lang = self._create_trans(None, 'it', True)
        self.assertFalse(self.video.is_complete, False)
        metadata_manager.update_metadata(self.video.pk)
        new_lang.save()
        self.video.subtitlelanguage_set.all().filter(percent_done=100).delete()
        self.assertFalse(self.video.is_complete)
            
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
        from videos.tasks import video_changed_tasks

        #test if fixtures has correct data
        langs_count = self.video.subtitlelanguage_set.filter(had_version=True).count()
        
        self.assertEqual(self.video.languages_count, langs_count)
        self.assertTrue(self.video.languages_count > 0)
        
        self.video.languages_count = 0
        self.video.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count)        
        
    def test_subtitle_language_save(self):
        self.assertEqual(self.video.complete_date, None)
        self.assertEqual(self.video.subtitlelanguage_set.count(), 1)

        self.language.is_complete = True
        self.language.save()
        from videos.tasks import video_changed_tasks
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.is_complete = False
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)
        
        #add one more SubtitleLanguage
        l = SubtitleLanguage(video=self.video)
        l.is_original = False
        l.is_complete = True
        l.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
# FIXME: Why should complete_date be non-null here?
#        self.assertNotEqual(self.video.complete_date, None)

        self.language.is_complete = True
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        l.is_complete = False
        l.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.is_complete = False
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)

        self.language.is_complete = True
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
                
        l.is_complete = True
        l.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)
        
        self.language.delete()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
# FIXME: why should complete_date be non-null here?
#        self.assertNotEqual(self.video.complete_date, None)

        l.delete()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)

from videos.feed_parser import FeedParser

class TestFeedParser(TestCase):
    #TODO: add test for MediaFeedEntryParser. I just can't find RSS link for it
    #RSS should look like this http://www.dailymotion.com/rss/ru/featured/channel/tech/1
    #but not from supported site
    youtube_feed_url_pattern =  'https://gdata.youtube.com/feeds/api/users/%s/uploads'
    youtube_username = 'universalsubtitles'
    
    mit_feed_url = 'http://ocw.mit.edu/rss/new/ocw_youtube_videos.xml'
    
    vimeo_feed_url = 'http://vimeo.com/blakewhitman/videos/rss'
    
    def setUp(self):
        pass

    def test_vimeo_feed_parsing(self):
        feed_parser = FeedParser(self.vimeo_feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, VimeoVideoType))
        
        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)
    
    def test_youtube_feed_parsing(self):
        feed_url = self.youtube_feed_url_pattern % self.youtube_username
        
        feed_parser = FeedParser(feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, YoutubeVideoType))
        
        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)
                
    def test_mit_feed_parsing(self):
        """
        If this test fails - try check few feed entries. Not all entries from
        MIT feed contain videos, so if sometime they delete some etries - test 
        can fail.
        """
        feed_parser = FeedParser(self.mit_feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, HtmlFiveVideoType))
        
        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)

# FIXME: this test is failing, and it looks like it's because of the feed.
#    def test_enclosure_parsing(self):
#        feed_url = 'http://webcast.berkeley.edu/media/common/rss/Computer_Science_10__001_Spring_2011_Video__webcast.rss'
#        
#        feed_parser = FeedParser(feed_url)
#        vt, info, entry = feed_parser.items().next()
#        self.assertTrue(isinstance(vt, HtmlFiveVideoType))
#        
#        video, created = Video.get_or_create_for_url(vt=vt)
#        self.assertTrue(video)            
        
    def test_dailymotion_feed_parsing(self):
        feed_url = 'http://www.dailymotion.com/rss/ru/featured/channel/tech/1'
        
        feed_parser = FeedParser(feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, DailymotionVideoType))
        
        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)        

class TestTemplateTags(TestCase):
    def setUp(self):
        from django.conf import settings
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }    
        from apps.testhelpers.views import _create_videos#, _create_team_videos
        fixture_path = os.path.join(settings.PROJECT_ROOT, "apps", "videos", "fixtures", "teams-list.json")
        data = json.load(open(fixture_path))
        self.videos = _create_videos(data, [])
        #self.team, created = Team.objects.get_or_create(name="test-team", slug="test-team")
        #self.tvs = _create_team_videos( self.team, self.videos, [self.user])
        
    def test_complete_indicator(self):
        from apps.videos.templatetags.subtitles_tags import complete_indicator
        # one original  complete
        l = SubtitleLanguage.objects.filter(is_original=True, is_complete=True)[0]
        self.assertEqual("100 %", complete_indicator(l))
        # one original non complete with 0 subs

        l = SubtitleLanguage.objects.filter(is_forked=True, is_complete=False)[0]
        self.assertEqual("0 Lines", complete_indicator(l))
        # one original noncomplete 2 subs
        l = SubtitleLanguage.objects.filter(video__title="6", is_original=True)[0]
        self.assertEqual("2 Lines", complete_indicator(l))
        # one trans non complete
        l = SubtitleLanguage.objects.filter(video__title="b", language='pt')[0]
        self.assertEqual("60 %", complete_indicator(l))
        

def _create_trans( video, latest_version=None, lang_code=None, forked=False):
        translation = SubtitleLanguage()
        translation.video = video
        translation.language = lang_code
        translation.is_original = False
        translation.is_forked = forked
        translation.save()
        v = SubtitleVersion()
        v.language = translation
        if latest_version:
            v.version_no = latest_version.version_no+1
        else:
            v.version_no = 1
        v.datetime_started = datetime.now()
        v.save()
        
        if latest_version is not None:
            for s in latest_version.subtitle_set.all():
                s.duplicate_for(v).save()
        return translation

