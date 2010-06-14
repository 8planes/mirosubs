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

from settings import *
from django.contrib.sites.models import Site

JS_USE_COMPILED = True

DEBUG = False
ADMINS = (
  ('Adam Duston', 'adam@8planes.com'),
  ('Hubert Huang', 'huberth@gmail.com'),
  ('Dmitriy', 'alerion.um@gmail.com')
)

SITE_ID = 7
SITE_NAME = 'mirosubs-staging-8planes'

TWITTER_CONSUMER_KEY = 'GmKbnjiW1fkzW0MraLKkiQ'
TWITTER_CONSUMER_SECRET = 'xgOc8kj0lH8AZkElPu5YgYAYz9QeLR16skHl5zA1ejg'

MEDIA_URL = "http://{0}/site_media/".format(Site.objects.get(id=SITE_ID).domain)
