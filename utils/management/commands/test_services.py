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

from django.core.management.base import BaseCommand
from django.conf import settings
from utils.redis_utils import default_connection
from haystack import backend
from haystack.query import SearchQuerySet
from pysolr import SolrError
from django.core.cache import cache
from utils.celery_search_index import update_search_index
from videos.models import Video
import random
import base64

class Command(BaseCommand):
    help = u'Test if Solr, Redis and Memcached are available'
    
    def handle(self, *args, **kwargs):
        self._test_redis()
        self._test_solr()
        self._test_memcached()
        
    def _test_redis(self):
        print '=== REDIS ==='
        assert default_connection.ping(), u'Redis is unavailable'

        val = str(random.random())
        key = 'test-redis-%s' % base64.b64encode(str(random.random()))
        
        default_connection.set(key, val)
        assert val == default_connection.get(key), u'Redis is unavailable. Can\'t get value'
        
        default_connection.delete(key)
        assert default_connection.get(key) is None, u'Redis is unavailable. Can\'t delete value'
                
        print 'OK'
        print
        
    def _test_solr(self):
        print '=== SOLR ==='
        sb = backend.SearchBackend()
        try:
            video = Video.objects.all()[:1].get()
            update_search_index(Video, video.pk)
            sb.conn.commit()
        except (IOError, SolrError), e:
            raise Exception('Solr is unavailable')
        except Video.DoesNotExist:
            raise Exception('Database is empty to test Solr')
        
        sqs = SearchQuerySet().filter(content=video.title)
        assert sqs, 'Solr is unavailable. Can\'t find video'
        
        print 'OK'
        print 
        
    def _test_memcached(self):
        print '=== CACHE ==='
        print 'backend: ', settings.CACHE_BACKEND
        val = random.random()
        key = 'test-cache-%s' % base64.b64encode(str(random.random()))
        
        cache.set(key, val)
        assert val == cache.get(key), u'Cache is unavailable. Can\'t get value' 
        
        cache.delete(key)
        assert cache.get(key) is None, u'Cache is unavailable. Can\'t delete value'
        
        print 'OK'
        print