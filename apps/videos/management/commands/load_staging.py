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
from django.core.management import call_command
from django.db.transaction import commit_on_success

class Command(BaseCommand):

    @commit_on_success
    def handle(self, *args, **kwargs):
        options = kwargs.get('options', {})
        fixtures = ['staging_users.json', 'staging_videos.json', 'staging_teams.json']
        for fx in fixtures:
            call_command('loaddata', fx, **options)
