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
from django.core.management import call_command
from haystack.query import SearchQuerySet
from videos.models import Video
from search.forms import SearchForm
from search.rpc import SearchApiClass
from auth.models import CustomUser as User
from utils.rpc import RpcMultiValueDict

def reset_solr():
    # cause the default site to load
    from haystack import site
    from haystack import backend
    sb = backend.SearchBackend()
    sb.clear()
    call_command('update_index')
    
class TestSearch(TestCase):
    fixtures = ['staging_users.json', 'staging_videos.json']
    titles = (
        u"Kisses in Romania's Food Market - Hairy Bikers Cookbook - BBC",
        u"Don't believe the hype - A Bit of Stephen Fry & Hugh Laurie - BBC comedy sketch",
        u"David Attenborough - Animal behaviour of the Australian bowerbird - BBC wildlife",
        u"JayZ talks about Beyonce - Friday Night with Jonathan Ross - BBC One",
        u"Amazing! Bird sounds from the lyre bird - David Attenborough  - BBC wildlife",
        u"Hans Rosling's 200 Countries, 200 Years, 4 Minutes - The Joy of Stats - BBC Four",
        u"HD: Grizzly Bears Catching Salmon - Nature's Great Events: The Great Salmon Run - BBC One",
        u"My Blackberry Is Not Working! - The One Ronnie, Preview - BBC One",
        u"Cher and Dawn French's Lookalikes - The Graham Norton Show preview - BBC One",
        u"Cute cheetah cub attacked by wild warthog - Cheetahs - BBC Earth"
    )    
    
    def setUp(self):
        self.user = User.objects.all()[0]
    
    def test_rpc(self):
        rpc = SearchApiClass()
        rdata = RpcMultiValueDict(dict(q=u'BBC'))
        
        for title in self.titles:
            video = Video.objects.all()[0]
            video.title = title
            video.save()
            reset_solr()
            
            result = rpc.search(rdata, self.user, testing=True)['sqs']
            self.assertTrue(video in [item.object for item in result], title)
        
    def test_search(self):
        reset_solr()
        sqs = SearchQuerySet().models(Video)
        qs = Video.objects.exclude(title='')
        self.assertTrue(qs.count())
        
        for video in qs:
            result = SearchForm.apply_query(video.title, sqs)
            self.assertTrue(video in [item.object for item in result])
            
    def test_search1(self):
        for title in self.titles:
            video = Video.objects.all()[0]
            sqs = SearchQuerySet().models(Video)
            video.title = title
            video.save()
            reset_solr()
            
            result = SearchForm.apply_query(video.title, sqs)
            self.assertTrue(video in [item.object for item in result], u"Failed to find video by title: %s" % title)
            
            result = SearchForm.apply_query(u'BBC', sqs)
            self.assertTrue(video in [item.object for item in result], u"Failed to find video by 'BBC' with title: %s" % title)              