"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from auth.models import CustomUser as User
from videos.models import Video, Action
from subrequests.models import SubtitleRequest

class TestSubtitleRequest(TestCase):

    fixtures = ['test.json']

    def setUp(self):
        self.video = Video.objects.all()[0]
        self.user = User.objects.get(username=u'admin')
        self.languages1 = ['en']
        self.languages2 = ['hi', 'fr']
        self.Model = SubtitleRequest.objects

    def test_create_request(self):
        request = self.Model.create_requests(self.video.video_id,
                                             self.user,
                                             self.languages1)[0]
        self.assertEqual(1, request.id)
        self.assertEqual(False, request.done)
        self.assertEqual(True, request.track)
        self.assertEqual(self.languages1[0], request.language)

        request.done = True
        request.save()

        self.Model.create_requests(self.video.video_id, self.user,
                                   self.languages1)

        request_count = SubtitleRequest.objects.filter(
                user=self.user,
                video=self.video,
                language=self.languages1[0]
        ).count()
        self.assertEqual(2, request_count)

        request = self.Model.create_requests(self.video.video_id,
                                             self.user,
                                             self.languages1)[0]
        # The request already existed so it must be marked as reopened
        self.assertEqual(False, request.done)


    def test_create_requests(self):
        self.Model.create_requests(self.video.video_id, self.user,
                                   self.languages1)
        requests = self.Model.create_requests(self.video.video_id, self.user,
                                              self.languages2)
        # Only two new requests should be created
        self.assertEqual(2, len(requests))

        # An action should have been created relating this video
        action = Action.objects.filter(subtitlerequests__in=requests).latest()
        self.assertEqual(2, action.subtitlerequests.all().count())

