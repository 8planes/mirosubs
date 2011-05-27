"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from videos import models
import os
import json
from django.conf import settings
from auth.models import CustomUser as User

class SimpleTest(TestCase):
    def test_create_videos(self):
        data = {
            "url": "http://www.example.com/sdf.mp4",
            "langs": [
                {
                    "code": "ar",
                    "num_subs": 0,
                    "is_complete": False,
                    "is_original": True,
                    "translations": []
                    },
                {
                    "code": "en",
                    "num_subs": 10,
                    "is_complete": True,
                    "is_original": False,
                    "translations": []
                    }], 
            "title": "c" }
        from apps.testhelpers.views import _create_videos
        videos = _create_videos([data], [])
        v = models.Video.objects.get(title='c')
        en = v.subtitle_language('en')
        self.assertTrue(en.is_forked)
        self.assertEquals('ar', v.subtitle_language().language)
