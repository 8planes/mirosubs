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
from auth.models import CustomUser as User
from time import sleep

class Command(BaseCommand):
    args = "<lang_code lang_code ...>"

    def handle(self, *args, **kwargs):
        file_name = 'users_{0}.csv'.format(''.join(args))
        with open(file_name, 'w') as f:
            self._write_users_to_file(f, args)

    def _write_users_to_file(self, file, langs):
        user_ids = set()
        for lang in langs:
            for user in User.objects.all():
                if user.speaks_language(lang) and user.id not in user_ids:
                    user_ids.add(user.id)
                    file.write('{0},{1},{2}\n'.format(user.id, user.username, user.email))
