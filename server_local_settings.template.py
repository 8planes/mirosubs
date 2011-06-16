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

DEV, STAGING, PRODUCTION = range(1, 4)

INSTALLATION = INSERT_INSTALLATION_HERE # one of DEV, STAGING, PRODUCTION

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

DATABASE_HOST = 'INSERT DB HOST'
DATABASE_NAME = 'INSERT DATABASE NAME'
DATABASE_PASSWORD = 'INSERT DATABASE PASSWORD'
DATABASE_USER = 'INSERT DATABASE USER'

DEFAULT_BUCKET = '' # special note: should be blank for dev.
HAYSTACK_SOLR_URL = 'http://localhost:38983/solr'
MEDIA_URL = 'http://dev.universalsubtitles.org/site_media/'
PROMOTE_TO_ADMINS = []

# SENTRY_* db settings only used on staging and production.
SENTRY_DATABASE_HOST = 'INSERT SENTRY DB HOST'
SENTRY_DATABASE_NAME = 'INSERT SENTRY DATABASE NAME'
SENTRY_DATABASE_PASSWORD = 'INSERT SENTRY DATABASE PASSWORD'
SENTRY_DATABASE_USER = 'INSERT SENTRY DATABASE USER'

TWITTER_CONSUMER_KEY = 'INSERT TWITTER CONSUMER KEY'
TWITTER_CONSUMER_SECRET = 'INSERT TWITTER CONSUMER SECRET'

VIMEO_API_KEY = 'INSERT VIMEO API KEY'
VIMEO_API_SECRET = 'INSERT VIMEO API SECRET'

RECAPTCHA_SECRET = ''
