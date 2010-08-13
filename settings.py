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

# Django settings for mirosubs project.
import os

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

gettext_noop = lambda s: s

from django.conf import global_settings
lang_dict = dict(global_settings.LANGUAGES)
lang_dict['es-ar'] = gettext_noop('Argentinian Spanish')
global_settings.LANGUAGES = tuple(i for i in lang_dict.items())

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'feedback@universalsubtitles.org'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': rel('mirosubs.sqlite3'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# 'embed{0}.js'.format(EMBED_JS_VERSION) gives the current embed script file name.
EMBED_JS_VERSION = ''
PREVIOUS_EMBED_JS_VERSIONS = []

JS_USE_COMPILED = False

# paths provided relative to media/js
JS_CORE = ['mirosubs.js', 
           'rpc.js',
           'unitofwork.js', 
           'clippy.js',
           'flash.js',
           'spinner.js',
           'sliderbase.js',
           'closingwindow.js',
           'video/video.js',
           'video/abstractvideoplayer.js',
           'video/html5videoplayer.js',
           'video/youtubevideoplayer.js',
           'video/flvvideoplayer.js',
           'video/videosource.js',
           'video/html5videosource.js',
           'video/youtubevideosource.js',
           'video/flvvideosource.js',
           'video/controlledvideoplayer.js',
           'widget/usersettings.js',
           'widget/logindialog.js',
           'widget/videotab.js',
           'widget/howtovideopanel.js',
           'widget/dialog.js',
           'widget/captionmanager.js',
           'widget/brokenwarning.js',
           'widget/mainmenu.js',
           'widget/rightpanel.js',
           'widget/basestate.js',
           'widget/unsavedwarning.js',
           'widget/subtitle/dialog.js',
           'widget/subtitle/msservermodel.js',
           'widget/subtitle/editablecaption.js',
           'widget/subtitle/editablecaptionset.js',
           'widget/subtitle/subtitlewidget.js',
           'widget/subtitle/addsubtitlewidget.js',
           'widget/subtitle/subtitlelist.js',
           'widget/subtitle/transcribeentry.js',
           'widget/subtitle/transcribepanel.js',
           'widget/subtitle/transcriberightpanel.js',
           'widget/subtitle/syncpanel.js',
           'widget/subtitle/reviewpanel.js',
           'widget/subtitle/sharepanel.js',
           'widget/subtitle/editpanel.js',
           'widget/subtitle/editrightpanel.js',
           'widget/subtitle/bottomfinishedpanel.js',
           'widget/timeline/timerow.js',
           'widget/timeline/timerowul.js',
           'widget/timeline/timelinesub.js',
           'widget/timeline/timelinesubs.js',
           'widget/timeline/timelineinner.js',
           'widget/timeline/timeline.js',
           'widget/timeline/subtitle.js',
           'widget/timeline/subtitleset.js',
           'widget/controls/bufferedbar.js',
           'widget/controls/playpause.js',
           'widget/controls/progressbar.js',
           'widget/controls/progressslider.js',
           'widget/controls/timespan.js',
           'widget/controls/videocontrols.js',
           'widget/controls/volumecontrol.js',
           'widget/controls/volumeslider.js',
           'widget/translate/dialog.js',
           'widget/translate/editdialog.js',
           'widget/translate/translationpanel.js',
           'widget/translate/translationlist.js',
           'widget/translate/translationwidget.js',
           'widget/translate/translationrightpanel.js',
           'widget/translate/editabletranslation.js',
           'widget/translate/servermodel.js',
           'widget/play/manager.js',
           'widget/widget.js']

JS_OFFSITE = list(JS_CORE)
JS_OFFSITE.append('widget/crossdomainembed.js')

JS_ONSITE = list(JS_CORE)
JS_ONSITE.append('widget/samedomainembed.js')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = rel('media')+'/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a9yr_yzp2vmj-2q1zq)d2+b^w(7fqu2o&jh18u9dozjbd@-$0!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'openid_consumer.middleware.OpenIDMiddleware',
)

ROOT_URLCONF = 'mirosubs.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
   rel('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'context_processors.current_site',
    'context_processors.current_commit',
    'context_processors.custom',
    'django.contrib.messages.context_processors.messages',
)

INSTALLED_APPS = (
    'auth',
    'django.contrib.auth',
    'socialauth',
    'openid_consumer',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'profiles',
    'sorl.thumbnail',
    'videos',
    'widget',
    'south',
    'haystack',
    'comments',
)

#Haystack configuration
HAYSTACK_SITECONF = 'search_site'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
SOLR_ROOT = rel('..', 'buildout', 'parts', 'solr', 'example')

# socialauth-related
OPENID_REDIRECT_NEXT = '/socialauth/openid/done/'

OPENID_SREG = {"required": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "http://axschema.org/contact/email", "count": 1, "required": True, "alias": "email"},
             {"type_uri": "fullname", "count": 1 , "required": False, "alias": "fullname"}]

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

AUTHENTICATION_BACKENDS = (
   'auth.backends.CustomUserBackend',
   'auth.backends.OpenIdBackend',
   'auth.backends.TwitterBackend',
   'auth.backends.FacebookBackend',
   'django.contrib.auth.backends.ModelBackend'
)

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = 'profiles.Profile'
ACCOUNT_ACTIVATION_DAYS = 9999 # we are using registration only to verify emails
SESSION_COOKIE_AGE = 2419200 # 4 weeks

RECENT_ACTIVITIES_ONPAGE = 10
ACTIVITIES_ONPAGE = 20
REVISIONS_ONPAGE = 20

FEEDBACK_EMAIL = 'universalsubtitles@pculture.org'
FEEDBACK_SUBJECT = 'Universal Subtitles Feedback'
FEEDBACK_RESPONSE_SUBJECT = 'Thanks for trying Universal Subtitles'
FEEDBACK_RESPONSE_EMAIL = 'universalsubtitles@pculture.org'
FEEDBACK_RESPONSE_TEMPLATE = 'feedback_response.html'

PROJECT_VERSION = '0.5'

EDIT_END_THRESHOLD = 120

GOOGLE_ANALYTICS_NUMBER = 'UA-xxxxxx-x'

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    LAST_COMMIT_GUID = ''
