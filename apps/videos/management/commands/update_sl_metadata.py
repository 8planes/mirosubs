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
from videos.models import SubtitleLanguage
from time import sleep

WAIT_BETWEEN_WRITES = 1

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print 'Run recalculate all sub langs count & percent done'
        all_count = SubtitleLanguage.objects.all().count() * 1.0
        updated = 0
        percent_done = 0
        for sl in SubtitleLanguage.objects.all():
            sl.update_percent_done()
            sl.update_complete_state()
            sleep(WAIT_BETWEEN_WRITES)
            updated += 1
            new_percent_done = int((updated / all_count) * 100)
            if new_percent_done != percent_done:
                print "%s%% done" % percent_done
                percent_done = new_percent_done
            
