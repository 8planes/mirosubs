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

# Note that this file is kept in .gitignore since it contains password information.

from settings import *
from passwords.unisubsdev import *

JS_USE_COMPILED = True

DEBUG = False
ADMINS = (
  ('Adam Duston', 'adam@8planes.com'),
  ('Dean Jansen', 'dean@pculture.org')
)

SITE_ID = 13
SITE_NAME = 'unisubsdev'

TWITTER_CONSUMER_KEY = 'Vbub5lMDc47d8cydMNCTQ'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'universalsubtitles_dev',
        'USER': 'univsubs_dev',
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': 'universalsubtitles.cxrucp2uira2.us-east-1.rds.amazonaws.com',
        'PORT': '3306'
}

MEDIA_URL = "http://dev.universalsubtitles.org/site_media/"
