from settings import *
import logging

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
    #filename = '/home/chad/src/ipa/log.txt',                                                                       
    #filename = 'w',                                                                                                
)
