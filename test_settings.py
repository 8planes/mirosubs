from settings import *
__import__('dev-settings', globals(), locals(), ['*'], -1)

ROOT_URLCONF = 'urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('mirosubs.sqlite3'), 
    }
}

INSTALLED_APPS += ('django_nose', )
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('mirosubs')
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'