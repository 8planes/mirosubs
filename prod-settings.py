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

JS_USE_COMPILED = True

DEBUG = False
ADMINS = (
  ('Rodrigo Guzman', 'rz@pybrew.com'),
  ('Adam Duston', 'adam@pybrew.com'),
)

DATABASE_NAME = '/var/www/universalsubtitles/mirosubs/mirosubs.sqlite3'
ROOT_URLCONF = 'mirosubs.urls'

SITE_ID = 8
SITE_NAME = 'mirosubs-prod'

# socialauth-related
OPENID_REDIRECT_NEXT = '/socialauth/openid/done/'

OPENID_SREG = {"required": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "http://axschema.org/contact/email", "count": 1, "required": True, "alias": "email"},
             {"type_uri": "fullname", "count": 1 , "required": False, "alias": "fullname"}]

TWITTER_CONSUMER_KEY = '568zigeMu0p0KNHI3XUn0g'
TWITTER_CONSUMER_SECRET = 'MihvLPmDl1PvBegfT1KVRqPNy4fTT2fyOb5SxzRJ0'

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )

LOGIN_REDIRECT_URL = '/'
