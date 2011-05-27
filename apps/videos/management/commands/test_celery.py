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
from videos.tasks import add
from optparse import make_option
import time

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--count', '-c', dest='count', type="int", help='Number of tasks', default=1000),
        make_option('--publisher', '-p', dest='use_publisher', action="store_true", 
                    default=False, help='Use one publisher for all tasks'),  
    )

    def handle(self, use_publisher, count, *args, **kwargs):
        if use_publisher:
            publisher = add.get_publisher() 
        
        start_t = time.time()
        
        for i in xrange(count):
            if i % 10 == 0:
                print '%s from %s' % (i, count)
            
            args = [i, i]
            
            if use_publisher:
                add.apply_async(args=args, publisher=publisher)
            else:
                add.apply_async(args=args)
        
        print time.time() - start_t