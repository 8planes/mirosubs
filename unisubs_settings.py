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

from server_local_settings import *

JS_USE_COMPILED = True

DEBUG = False
ADMINS = (
  ('Adam Duston', 'adam@8planes.com'),
  ('Holmes Wilson', 'hwilson@gmail.com'),
  ('usubs-errors', 'usubs-errors@pculture.org')
)

HAYSTACK_SOLR_URL = 'http://localhost:8983/solr'
SOLR_ROOT = "/usr/local/apache-solr-1.3.0/example"

if INSTALLATION == DEV:
    SITE_ID = 13
    SITE_NAME = 'unisubsdev'
    FEEDBACK_EMAILS.append('aduston@gmail.com')
    TWITTER_CONSUMER_KEY = 'Vbub5lMDc47d8cydMNCTQ'
    VIMEO_API_KEY = 'e1a46f832f8dfa99652781ee0b39df12'
    MEDIA_URL = 'http://dev.universalsubtitles.org/site_media/'
    REDIS_DB = "3"
    AWS_QUEUE_PREFIX = 'DEV'
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
    EMAIL_SUBJECT_PREFIX = '[usubs-dev]'
elif INSTALLATION == STAGING:
    SITE_ID = 14
    SITE_NAME = 'unisubsstaging'
    TWITTER_CONSUMER_KEY = 'XYDDYlf54CU9bKMfIbvgNg'
    VIMEO_API_KEY = 'e1a46f832f8dfa99652781ee0b39df12'
    MEDIA_URL = 'http://s3.staging.universalsubtitles.org/'
    REDIS_DB = "2"
    AWS_QUEUE_PREFIX = 'STAGING'
    CACHE_BACKEND = 'memcached://ip-10-124-229-117.ec2.internal:61211/'
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    # TODO: insert tracelyzer stuff here.
    EMAIL_SUBJECT_PREFIX = '[usubs-staging]'
elif INSTALLATION == PRODUCTION:
    SITE_ID = 8
    SITE_NAME = 'unisubs'
    TWITTER_CONSUMER_KEY = '568zigeMu0p0KNHI3XUn0g'
    VIMEO_API_KEY = 'e1a46f832f8dfa99652781ee0b39df12'
    MEDIA_URL = 'http://s3.www.universalsubtitles.org/'
    REDIS_DB = "1"
    AWS_QUEUE_PREFIX = 'PRODUCTION'
    CACHE_BACKEND = 'memcached://ip-10-124-229-117.ec2.internal:11211/'
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    EMAIL_SUBJECT_PREFIX = '[usubs-production]'

IGNORE_REDIS = True

ALARM_EMAIL = FEEDBACK_EMAILS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': '3306'
        }
    }

USE_AMAZON_S3 = AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and DEFAULT_BUCKET

BROKER_USER = AWS_ACCESS_KEY_ID
BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY
BROKER_VHOST = AWS_QUEUE_PREFIX

EMAIL_BCC_LIST = ['hwilson+notifications@gmail.com']

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    LAST_COMMIT_GUID = ''
    
try:
    from settings_local import *
except ImportError:
    pass