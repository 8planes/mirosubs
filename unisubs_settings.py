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
import logging

#INSTALLED_APPS += (
#    'djcelery',
#)
#CELERY_RESULT_BACKEND = 'redis'

JS_USE_COMPILED = True

DEV = True

DEBUG = False

SITE_ID = 13
SITE_NAME = 'unisubsdev'

if DEV:
   FEEDBACK_EMAILS.append('aduston@gmail.com')

EMAIL_SUBJECT_PREFIX = '[{0}]'.format(SITE_NAME)

TWITTER_CONSUMER_KEY = 'Vbub5lMDc47d8cydMNCTQ'
TWITTER_CONSUMER_SECRET = 'Fb2ClDQTfHFe9lAYgrZP3IFoO56jL9gg2OfRmUyxTA'

#Video API keys
VIMEO_API_KEY = 'e1a46f832f8dfa99652781ee0b39df12'
VIMEO_API_SECRET = 'bdaeb531298eeee1'

MEDIA_URL = "http://dev.universalsubtitles.org/site_media/"

REDIS_DB = "3"

USE_AMAZON_S3 = False

EMAIL_BCC_LIST = ['hwilson+notifications@gmail.com']

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    LAST_COMMIT_GUID = ''
