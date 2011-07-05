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
from utils.redis_utils import default_connection
from haystack import backend
from pysolr import SolrError
from django.core.cache import cache

class Command(BaseCommand):
    help = u'Test if Solr, Redis and Memcached are available'
    
    def handle(self, *args, **kwargs):
        self._test_redis()
        self._test_solr()
        self._test_memcached()
        
    def _test_redis(self):
        assert default_connection.ping(), u'Redis is unavailable'
        
        print 'Redis: OK'
        
    def _test_solr(self):
        sb = backend.SearchBackend()
        try:
            sb.conn.commit()
        except (IOError, SolrError), e:
            raise Exception('Solr is unavailable')
        
        print 'Solr: OK'
        
    def _test_memcached(self):
        val = 1
        key = 'test-cache'
        cache.set(key, val)
        assert val == cache.get(key), u'Cache is unavailable'
        
        print 'Cache: OK'