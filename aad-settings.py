from settings import *
import logging

SITE_ID = 4
SITE_NAME = 'mirosubs-dev'


# socialauth-related
OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_SREG = {"requred": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "email", "count": 1, "required": False, "alias": "email"}, {"type_uri": "fullname", "count":1 , "required": False, "alias": "fullname"}]

TWITTER_CONSUMER_KEY = '6lHYqtxzQBD3lQ55Chi6Zg'
TWITTER_CONSUMER_SECRET = 'ApkJPIIbBKp3Wph0JBoAg2Nsk1Z5EG6PFTevNpd5Y00'

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )
