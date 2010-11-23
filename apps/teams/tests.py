# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from os import path
from django.conf import settings
from teams.models import Team
from videos.models import Video, VIDEO_TYPE_YOUTUBE

class TeamsTest(TestCase):
    
    fixtures = ["test.json"]
    
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }
    
    def test_views(self):
        self.client.login(**self.auth)
        
        response = self.client.get(reverse("teams:create"))
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "description": u"",
            "video_url": u"",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team",
            "name": u"New team"
        }
        response = self.client.post(reverse("teams:create"), data)
        self.failUnlessEqual(response.status_code, 302)
        team = Team.objects.get(slug=data['slug'])
        
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit_logo", kwargs={"pk": team.pk})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 200)
        team = Team.objects.get(pk=team.pk)
        self.assertTrue(team.logo)
        
        data = {
            "name": u"New team",
            "video_url": u"http://www.youtube.com/watch?v=tGsHDUdw8As",
            "membership_policy": u"4",
            "video_policy": u"1",
            "description": u"",
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 302)
        video = Video.objects.get(videourl__type=VIDEO_TYPE_YOUTUBE, videourl__videoid='tGsHDUdw8As')
        team = Team.objects.get(pk=team.pk)
        self.assertEqual(team.video, video)
        
        url = reverse("teams:edit_members", kwargs={"pk": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:edit_videos", kwargs={"pk": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:applications", kwargs={"pk": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        url = reverse("teams:detail", kwargs={"slug": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)        

    def test_fixes(self):
        url = reverse("teams:detail", kwargs={"slug": 'slug-does-not-exist'})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)