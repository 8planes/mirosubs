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
from auth.models import CustomUser as User
from videos.models import Video

class TestModels(TestCase):
    
    #fixtures = ['test.json']
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
    def setUp(self):
        self.video = Video.objects.exclude(subtitlelanguage=None)[:1].get()
        self.video.followers = []
        self.sl = self.video.subtitlelanguage_set.all()[:1].get()
        self.sl.followers = []
        
        self.ovideo = Video.objects.exclude(subtitlelanguage=None).exclude(pk=self.video.pk)[:1].get()
        self.ovideo.followers = []
        self.osl = self.ovideo.subtitlelanguage_set.all()[:1].get()
        self.osl.followers = []
        
        self.user = User.objects.all()[:1].get()
        
    def test_videos_updating_1(self):
        self.assertEqual(self.video.followers.count(), 0)
        self.assertEqual(self.ovideo.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)
        
        self.video.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])
        
        self.ovideo.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])
        
        self.video.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])
        
        self.ovideo.followers = []
        self.assertEqual(self.user.videos.count(), 0)
        
        self.user.followed_videos.add(self.video)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])
        
        self.user.followed_videos.add(self.ovideo)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])
        
        self.user.followed_videos.remove(self.video)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])
        
        self.user.followed_videos = []
        self.assertEqual(self.user.videos.count(), 0)
        
    def test_videos_updating_2(self):
        self.assertEqual(self.video.followers.count(), 0)
        self.assertEqual(self.ovideo.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)
        
        self.video.followers.add(self.user)
        self.ovideo.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])
        
        self.sl.followers.add(self.user)
        self.video.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])
        
        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])
        
        self.ovideo.followers = []
        self.assertEqual(self.user.videos.count(), 0)
        
        self.sl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])
        
        self.video.followers.add(self.user)
        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])
        
        self.video.followers.remove(self.user)
        self.assertEqual(self.user.videos.count(), 0)
        
    def test_videos_updating_3(self):
        self.assertEqual(self.sl.followers.count(), 0)
        self.assertEqual(self.osl.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)
        
        self.sl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id])
        
        self.osl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id, self.osl.video.id])
        
        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.osl.video.id])
        
        self.osl.followers = []
        self.assertEqual(self.user.videos.count(), 0)
        
        self.user.followed_languages.add(self.sl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id])
        
        self.user.followed_languages.add(self.osl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id, self.osl.video.id])
        
        self.user.followed_languages.remove(self.sl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.osl.video.id])
        
        self.user.followed_languages = []
        self.assertEqual(self.user.videos.count(), 0)        