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
