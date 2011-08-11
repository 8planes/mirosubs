"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from auth.models import CustomUser as User
from videos.tasks import video_changed_tasks
from videos.models import Video, SubtitleLanguage

from subrequests.models import SubtitleRequest

SubRequests = SubtitleRequest.objects

class TestSubtitleRequest(TestCase):

    fixtures = ['test.json']
    langs = ['en', 'hi', 'fr', 'ca']

    def setUp(self):
        self.video = Video.objects.all()[0]
        self.user = User.objects.get(username=u'admin')
        self.DEFAULTS = {
            'description': 'A request description just for test',
            'track': True,
        }
        video_changed_tasks.delay(self.video)

    def _create_requests(self, langs, **kwargs):
        '''
        Create a test request
        '''
        d = dict(self.DEFAULTS, **kwargs)
        return  SubRequests.create_requests(self.video.video_id, self.user,
                                            langs, d['track'],
                                            d['description'])
    def _lang_requests(self, language):
        '''
        Get all test requests for a langauge
        '''
        return self.video.subtitlerequest_set.filter(user=self.user,
                                                     language=language)

    def test_create_requests(self):
        '''
        Test creation of a simple request for subtitles.
        '''
        subreqs = self._create_requests(self.langs[:2])
        self.assertEqual(2, len(subreqs))

        # Test action field
        for subreq in subreqs:
            self.assertEqual(not subreq.action, False)
            self.assertEqual(subreq.description, self.DEFAULTS['description'])
            self.assertEqual(subreq.track, self.DEFAULTS['track'])

    def test_rerequest_same(self):
        '''
        If user creates request with same parameters again, no new one should
        be created
        '''
        lang = self.langs[:1]
        self.assertEqual(self._create_requests(lang)[0],
                         self._create_requests(lang)[0])

    def test_rerequest_new(self):
        '''
        If user creates request with different parameters again.
        '''
        lang = self.langs[1:2]
        req1 = self._create_requests(lang, description="")[0]
        req2 = self._create_requests(lang)[0]

        # The requests should not be the same
        self.assertEqual(req1!=req2, True)

        # All the older requests should have been marked as done
        for request in self._lang_requests(lang[0]).exclude(pk=req2.pk):
            self.assertEqual(request.done, True)

    def test_request_language_handler(self):
        '''
        Test the signal handler which sets the requesters as language
        followers when a new (requested) language is created.
        '''

        subrequest = self._create_requests(self.langs[2:3])[0]

        # Test if the user automatically starts following
        # a language if there is a pending request
        original = self.video.subtitle_language()
        newlang = SubtitleLanguage(
            video=self.video,
            language=subrequest.language,
            is_original=False,
            is_forked=False,
            standard_language=original)
        newlang.save()

        self.assertEqual(self.user, newlang.followers.all()[0])

        # Test if subtitle request is marked as done
        newlang.is_complete = True
        newlang.save()
        subrequest = SubtitleRequest.objects.get(pk=subrequest.pk)

        self.assertEqual(subrequest.done, True)
