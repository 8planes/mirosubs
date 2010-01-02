from settings import *
import logging

SITE_ID = 3
SITE_NAME = 'mirosubs-rz'

INSTALLED_APPS +=(
    'django_extensions',
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
 
OPENID_SREG = {"requred": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "email", "count": 1, "required": False, "alias": "email"}, {"type_uri": "fullname", "count":1 , "required": False, "alias": "fullname"}]

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
