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
from statistic import st_widget_view_statistic
from videos.models import Video
from utils.redis_utils import default_connection
import time

class Command(BaseCommand):
    help = 'This command "view" 1000 videos widget and then migrate data to DB and uddate search index'
    
    def handle(self, *args, **kwargs):
        if default_connection.ping() is None:
            print 'Redis is unavailable.'
            return
        
        start = time.time()
        
        qs = Video.objects.all()[:1000]
        
        print '"View" videos'
        i = 0
        for video in qs:
            i += 1
            if i % 100 == 0:
                print 'Viewed %s' % i
                
            st_widget_view_statistic.update(video=video)
            
        print ''
        print 'Migrate to DB'
        st_widget_view_statistic.migrate(verbosity=2)
        
        print 'Test migrated data'
        for video in qs:
            views_st = st_widget_view_statistic.get_views(video=video)
            assert video.widget_views_count >= views_st['month'], video.pk
        
        print time.time() - start