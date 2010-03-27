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
import logging

DEBUG = True

from socket import gethostname
if gethostname() == 'lrz2':
    SITE_ID = 3
    SITE_NAME = 'mirosubs-rz'
#if gethostname() == 'rz-laptopII-ub' or gethostname == 'rz-laptop-ub':
SITE_ID = 5
SITE_NAME = 'mirosubs-rz-local'

INSTALLED_APPS +=(
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)s %(asctime)s %(filename)s:%(lineno)s %(funcName)s\n%(message)s\n',
)

# socialauth-related
OPENID_REDIRECT_NEXT = '/socialauth/openid/done/'
 
OPENID_SREG = {"required": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "http://axschema.org/contact/email", "count": 1, "required": True, "alias": "email"},
             {"type_uri": "fullname", "count":1 , "required": False, "alias": "fullname"}]

TWITTER_CONSUMER_KEY = 'GRcOIZyWRM0XxluS6flA'
TWITTER_CONSUMER_SECRET = '4BSIzc524xOV9edjyXgJiae1krY7TEmG38K7tKohc'

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''
 
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )
 
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'localhost'
EMAIL_PORT = '1025'
