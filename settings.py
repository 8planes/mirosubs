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

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

def rel(*x):
    return os.path.join(PROJECT_ROOT, *x)

gettext_noop = lambda s: s

from django.conf import global_settings
lang_dict = dict(global_settings.LANGUAGES)
lang_dict['es-ar'] = gettext_noop(u'Spanish, Argentinian')
lang_dict['en-gb'] = gettext_noop(u'English, British')
lang_dict['pt-br'] = gettext_noop(u'Portuguese, Brazilian')
lang_dict['sr-latn'] = gettext_noop(u'Latin, Serbian')
lang_dict['zh-cn'] = gettext_noop(u'Chinese, Simplified')
lang_dict['zh-tw'] = gettext_noop(u'Chinese, Traditional')
lang_dict['eo'] = gettext_noop(u'Esperanto')
global_settings.LANGUAGES = tuple(i for i in lang_dict.items())

METADATA_LANGUAGES = (
    ('meta-tw', 'Metadata: Twitter'),
    ('meta-geo', 'Metadata: Geo'),
    ('meta-wiki', 'Metadata: Wikipedia'),
)

ALL_LANGUAGES = list(global_settings.LANGUAGES)
ALL_LANGUAGES.extend(METADATA_LANGUAGES)
ALL_LANGUAGES = dict(ALL_LANGUAGES)
ALL_LANGUAGES['iu'] = gettext_noop(u'Inuktitut')
ALL_LANGUAGES['moh'] = gettext_noop(u'Mohawk')
ALL_LANGUAGES['oji'] = gettext_noop(u'Anishinaabe')
ALL_LANGUAGES['cr'] = gettext_noop(u'Cree')
ALL_LANGUAGES['hai'] = gettext_noop(u'Haida')
ALL_LANGUAGES['ase'] = gettext_noop(u'American Sign Language')
ALL_LANGUAGES['wol'] = gettext_noop(u'Wolof')
ALL_LANGUAGES['que'] = gettext_noop(u'Quechua')
ALL_LANGUAGES['swa'] = gettext_noop(u'Swahili')
ALL_LANGUAGES['urd'] = gettext_noop(u'Urdu')
ALL_LANGUAGES['pan'] = gettext_noop(u'Punjabi')
ALL_LANGUAGES['br'] = gettext_noop(u'Breton')
ALL_LANGUAGES['be'] = gettext_noop(u'Belarusian')
ALL_LANGUAGES['ber'] = gettext_noop(u'Berber')
ALL_LANGUAGES['hau'] = gettext_noop(u'Hausa')
ALL_LANGUAGES['orm'] = gettext_noop(u'Oromo')
ALL_LANGUAGES['zul'] = gettext_noop(u'Zulu')
ALL_LANGUAGES['som'] = gettext_noop(u'Somali')
ALL_LANGUAGES['yor'] = gettext_noop(u'Yoruba')
ALL_LANGUAGES['ibo'] = gettext_noop(u'Igbo')
ALL_LANGUAGES['af'] = gettext_noop(u'Afrikaans')
ALL_LANGUAGES['kin'] = gettext_noop(u'Kinyarwanda')
ALL_LANGUAGES['amh'] = gettext_noop(u'Amharic')
ALL_LANGUAGES['sna'] = gettext_noop(u'Shona')
ALL_LANGUAGES['bam'] = gettext_noop(u'Bambara')
ALL_LANGUAGES['aka'] = gettext_noop(u'Akan')
ALL_LANGUAGES['bnt'] = gettext_noop(u'Ibibio')
ALL_LANGUAGES['ful'] = gettext_noop(u'Fula')
ALL_LANGUAGES['mlg'] = gettext_noop(u'Malagasy')
ALL_LANGUAGES['lin'] = gettext_noop(u'Lingala')
ALL_LANGUAGES['nya'] = gettext_noop(u'Chewa')
ALL_LANGUAGES['xho'] = gettext_noop(u'Xhosa')
ALL_LANGUAGES['kon'] = gettext_noop(u'Kongo')
ALL_LANGUAGES['tir'] = gettext_noop(u'Tigrinya')
ALL_LANGUAGES['luo'] = gettext_noop(u'Luo')
ALL_LANGUAGES['lua'] = gettext_noop(u'Luba-Kasai')
ALL_LANGUAGES['kik'] = gettext_noop(u'Gikuyu')
ALL_LANGUAGES['mos'] = gettext_noop(u'Mossi')
ALL_LANGUAGES['sot'] = gettext_noop(u'Sotho')
ALL_LANGUAGES['luy'] = gettext_noop(u'Luhya')
ALL_LANGUAGES['tsn'] = gettext_noop(u'Tswana')
ALL_LANGUAGES['kau'] = gettext_noop(u'Kanuri')
ALL_LANGUAGES['umb'] = gettext_noop(u'Umbundu')
ALL_LANGUAGES['nso'] = gettext_noop(u'Northern Sotho')
ALL_LANGUAGES['mnk'] = gettext_noop(u'Mandinka')
ALL_LANGUAGES['ky'] = gettext_noop(u'Kyrgyz')
ALL_LANGUAGES['mr'] = gettext_noop(u'Marathi')
ALL_LANGUAGES['ml'] = gettext_noop(u'Malayalam')
ALL_LANGUAGES['or'] = gettext_noop(u'Oriya')
ALL_LANGUAGES['gu'] = gettext_noop(u'Gujarati')
ALL_LANGUAGES['as'] = gettext_noop(u'Assamese')
ALL_LANGUAGES['tl'] = gettext_noop(u'Filipino')
ALL_LANGUAGES['si'] = gettext_noop(u'Sinhala')
ALL_LANGUAGES['zh'] = gettext_noop(u'Chinese, Yue')
ALL_LANGUAGES['oc'] = gettext_noop(u'Occitan')
ALL_LANGUAGES['ht'] = gettext_noop(u'Creole, Haitian')
ALL_LANGUAGES['ne'] = gettext_noop(u'Nepali')
ALL_LANGUAGES['ee'] = gettext_noop(u'Ewe')
ALL_LANGUAGES['ms'] = gettext_noop(u'Malay')
ALL_LANGUAGES['yi'] = gettext_noop(u'Yiddish')
ALL_LANGUAGES['my'] = gettext_noop(u'Burmese')
ALL_LANGUAGES['bo'] = gettext_noop(u'Tibetan')
ALL_LANGUAGES['ast'] = gettext_noop(u'Asturian')
ALL_LANGUAGES['ay'] = gettext_noop(u'Aymara')
ALL_LANGUAGES['ps'] = gettext_noop(u'Pashto')
ALL_LANGUAGES['lkt'] = gettext_noop(u'Lakota')

del ALL_LANGUAGES['no']
ALL_LANGUAGES = tuple(i for i in ALL_LANGUAGES.items())

# languages that more people speak, and therefore
# are it's translators are not as rare
LINGUA_FRANCAS = ["en", "en-gb"]

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PISTON_EMAIL_ERRORS = True
PISTON_DISPLAY_ERRORS = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

ALARM_EMAIL = None
MANAGERS = ADMINS

P3P_COMPACT = 'CP="CURa ADMa DEVa OUR IND DSP CAO COR"'

DEFAULT_FROM_EMAIL = '"Universal Subtitles" <feedback@universalsubtitles.org>'
WIDGET_LOG_EMAIL = 'widget-logs@universalsubtitles.org'

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

CSS_USE_COMPILED = True
JS_USE_COMPILED = False

USE_BUNDLED_MEDIA = not DEBUG

COMPRESS_YUI_BINARY = "java -jar ./css-compression/yuicompressor-2.4.6.jar"
COMPRESS_OUTPUT_DIRNAME = "static-cache"


USER_LANGUAGES_COOKIE_NAME = 'unisub-languages-cookie'

# paths provided relative to media/js
JS_CORE = \
    ['mirosubs.js', 
     'rpc.js',
     'clippy.js',
     'flash.js',
     'spinner.js',
     'sliderbase.js',
     'closingwindow.js',
     'loadingdom.js',
     'tracker.js',
     'style.js',
     'messaging/simplemessage.js',
     'video/video.js',
     'video/captionview.js',
     'video/abstractvideoplayer.js',
     'video/flashvideoplayer.js',
     'video/html5videoplayer.js',
     'video/youtubevideoplayer.js',
     'video/jwvideoplayer.js',
     'video/flvvideoplayer.js',
     'video/videosource.js',
     'video/html5videosource.js',
     'video/youtubevideosource.js',
     'video/brightcovevideosource.js',
     'video/brightcovevideoplayer.js',
     'video/flvvideosource.js',
     'video/bliptvplaceholder.js',
     'video/controlledvideoplayer.js',
     'video/vimeovideosource.js',
     'video/vimeovideoplayer.js',
     'video/dailymotionvideosource.js',
     'video/dailymotionvideoplayer.js',
     'startdialog/model.js',
     'startdialog/videolanguage.js',
     'startdialog/videolanguages.js',
     'startdialog/tolanguage.js',
     'startdialog/tolanguages.js',
     'startdialog/dialog.js',
     'requestdialog.js',
     'widget/subtitle/editablecaption.js',
     "widget/subtitle/editablecaptionset.js",
     'widget/usersettings.js',
     'widget/logindialog.js',
     'widget/videotab.js',
     'widget/howtovideopanel.js',
     'widget/dialog.js',
     'widget/captionmanager.js',
     'widget/rightpanel.js',
     'widget/basestate.js',
     'widget/subtitlestate.js',
     'widget/dropdowncontents.js',
     'widget/playcontroller.js',
     'widget/subtitlecontroller.js',
     'widget/subtitledialogopener.js',
     'widget/opendialogargs.js',
     'widget/dropdown.js',
     'widget/play/manager.js',
     'widget/widgetcontroller.js',
     'widget/widget.js',
     'widget/subtitle/onsaveddialog.js',
]

JS_DIALOG = \
    ['subtracker.js',
     'srtwriter.js',
     'widget/unsavedwarning.js',
     'widget/resumeeditingrecord.js',
     'widget/droplockdialog.js',
     'finishfaildialog/dialog.js',
     'finishfaildialog/errorpanel.js',
     'finishfaildialog/reattemptuploadpanel.js',
     'finishfaildialog/copydialog.js',
     'widget/subtitle/dialog.js',
     'widget/subtitle/msservermodel.js',
     'widget/subtitle/subtitlewidget.js',
     'widget/subtitle/addsubtitlewidget.js',
     'widget/subtitle/subtitlelist.js',
     'widget/subtitle/transcribeentry.js',
     'widget/subtitle/transcribepanel.js',
     'widget/subtitle/transcriberightpanel.js',
     'widget/subtitle/syncpanel.js',
     'widget/subtitle/reviewpanel.js',
     'widget/subtitle/reviewrightpanel.js',
     'widget/subtitle/sharepanel.js',
     'widget/subtitle/completeddialog.js',
     'widget/subtitle/editpanel.js',
     'widget/subtitle/editrightpanel.js',
     'widget/subtitle/bottomfinishedpanel.js',
     'widget/subtitle/logger.js',
     'widget/subtitle/savedsubtitles.js',
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
     'widget/translate/googletranslator.js',
     'widget/translate/dialog.js',
     'widget/translate/translationpanel.js',
     'widget/translate/translationlist.js',
     'widget/translate/translationwidget.js',
     'widget/translate/translationrightpanel.js',
     'widget/translate/forkdialog.js',
     'widget/translate/titletranslationwidget.js']

JS_OFFSITE = list(JS_CORE)
JS_OFFSITE.append('widget/crossdomainembed.js')

JS_ONSITE = list(JS_CORE)
JS_ONSITE.extend(
    ['srtwriter.js',
     'widget/samedomainembed.js',
     "widget/api/servermodel.js",
     "widget/api/api.js"])

JS_WIDGETIZER_CORE = list(JS_CORE)
JS_WIDGETIZER_CORE.extend([
    "widget/widgetdecorator.js",
    "widgetizer/videoplayermaker.js",
    "widgetizer/widgetizer.js",
    "widgetizer/youtube.js",
    "widgetizer/html5.js",
    "widgetizer/jwplayer.js"])

JS_WIDGETIZER = list(JS_WIDGETIZER_CORE)
JS_WIDGETIZER.append('widgetizer/dowidgetize.js')

JS_EXTENSION = list(JS_WIDGETIZER_CORE)
JS_EXTENSION.append('widgetizer/extension.js')

JS_API = list(JS_CORE)
JS_API.extend(JS_DIALOG)
JS_API.extend([
        "widget/api/servermodel.js",
        "widget/api/api.js"])

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
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)


MIDDLEWARE_CLASSES = (
    'middleware.ResponseTimeMiddleware',
    'utils.ajaxmiddleware.AjaxErrorMiddleware',
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'openid_consumer.middleware.OpenIDMiddleware',
    'middleware.P3PHeaderMiddleware',
    'middleware.UserUUIDMiddleware',
    'middleware.SaveUserIp',
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
    'context_processors.user_languages',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n'
)

INSTALLED_APPS = (
    'auth',
    'django.contrib.auth',
    'localeurl',
    'socialauth',
    'openid_consumer',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.webdesign',
    'django_extensions',
    'profiles',
    'sorl.thumbnail',
    'videos',
    'teams',
    'widget',
    'uslogging',
    'south',
    'haystack',
    'comments',
    'messages',
    'statistic',
    'search',
    'api',
    'utils',
    'targetter',
    'livesettings',
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    'djcelery',
    'rosetta',
    'testhelpers',
    'unisubs_compressor',
    'subrequests',
    'mirosubs' #dirty hack to fix http://code.djangoproject.com/ticket/5494 ,
)

# Celery settings

# import djcelery
# djcelery.setup_loader()

# For running worker use: python manage.py celeryd -E --concurrency=10 -n worker1.localhost
# Run event cather for monitoring workers: python manage.py celerycam --frequency=5.0
# This allow know are workers online or not: python manage.py celerybeat

CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_SEND_EVENTS = False
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_RESULT_BACKEND = 'redis'

BROKER_BACKEND = 'kombu_backends.amazonsqs.Transport'
BROKER_USER = AWS_ACCESS_KEY_ID = ""
BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY = ""
BROKER_VHOST = AWS_QUEUE_PREFIX = 'UNISUB' #Prefix for queues, should be DEV or STAGING 

#################

import re
LOCALE_INDEPENDENT_PATHS = (
    re.compile('^/widget'),
    re.compile('^/api'),
    re.compile('^/jstest'),
    re.compile('^/sitemap.*.xml'),
    re.compile('^/crossdomain.xml'),
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

VIMEO_API_KEY = None
VIMEO_API_SECRET = None

AUTHENTICATION_BACKENDS = (
   'auth.backends.CustomUserBackend',
   'auth.backends.OpenIdBackend',
   'auth.backends.TwitterBackend',
   'auth.backends.FacebookBackend',
   'django.contrib.auth.backends.ModelBackend',
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

FEEDBACK_EMAIL = 'socmedia@pculture.org'
FEEDBACK_EMAILS = [FEEDBACK_EMAIL, 'hwilson@gmail.com']
FEEDBACK_ERROR_EMAIL = 'universalsubtitles-errors@pculture.org'
FEEDBACK_SUBJECT = 'Universal Subtitles Feedback'
FEEDBACK_RESPONSE_SUBJECT = 'Thanks for trying Universal Subtitles'
FEEDBACK_RESPONSE_EMAIL = 'universalsubtitles@pculture.org'
FEEDBACK_RESPONSE_TEMPLATE = 'feedback_response.html'

#teams
TEAMS_ON_PAGE = 12

PROJECT_VERSION = '0.5'

EDIT_END_THRESHOLD = 120

ANONYMOUS_USER_ID = -1

#Use on production
GOOGLE_ANALYTICS_NUMBER = 'UA-163840-22'
MIXPANEL_TOKEN = '44205f56e929f08b602ccc9b4605edc3'

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    print "deploy/create_commit_file must be ran before boostrapping django"
    raise

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DEFAULT_BUCKET = ''
USE_AMAZON_S3 = AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and DEFAULT_BUCKET

AVATAR_MAX_SIZE = 500*1024
THUMBNAILS_SIZE = (
    (100, 100),
    (50, 50)
)

EMAIL_BCC_LIST = []

CACHE_BACKEND = 'locmem://'

#for mirosubs.example.com
RECAPTCHA_PUBLIC = '6LdoScUSAAAAANmmrD7ALuV6Gqncu0iJk7ks7jZ0'
RECAPTCHA_SECRET = ' 6LdoScUSAAAAALvQj3aI1dRL9mHgh85Ks2xZH1qc'

ROSETTA_EXCLUDED_APPLICATIONS = (
    'livesettings',
    'openid_consumer',
    'rosetta'
)

# paths from MEDIA URL
MEDIA_BUNDLES = {

    "base": {
        "type":"css",
        "files" : (
            "css/jquery.jgrowl.css",
            "css/jquery.alerts.css",
            "css/960.css",
            "css/reset.css",
            "css/html.css", 
            "css/about_faq.css", 
            "css/breadcrumb.css", 
            "css/buttons.css", 
            "css/classes.css", 
            "css/comments.css", 
            "css/forms.css",
            "css/index.css",
            "css/layout.css",
            "css/profile_pages.css", 
            "css/revision_history.css",
            "css/teams.css", 
            "css/transcripts.css", 
            "css/background.css", 
            "css/activity_stream.css", 
            "css/settings.css", 
            "css/feedback.css", 
            "css/messages.css", 
            "css/global.css", 
            "css/top_user_panel.css", 
            "css/services.css", 
            "css/solutions.css",
            "css/watch.css",
          ),
        },
    "video_history":{
        "type":"css",
        "files":(
               "css/mirosubs-widget.css" ,
               "css/nyroModal.css",
               "css/dev.css"
         ),
        },

    "home":{
        "type":"css",
        "files":(
            "css/nyroModal.css",
            "css/mirosubs-widget.css",

         ),
        },
    "mirosubs-offsite-compiled":{
        "type": "js",
        "files": JS_OFFSITE,
        },

    "mirosubs-onsite-compiled":{
        "type": "js",
        "files": JS_ONSITE,
     },
     "mirosubs-widgetizer":{
        "type": "js",
        "files": ["config.js"] + JS_WIDGETIZER,
     },
    "mirosubs-widgetizer-debug":{
        "type": "js",
        "files": ["config.js" ] + JS_WIDGETIZER,
        "debug": True,
     },
    "mirosubs-extension":{
        "type": "js",
        "files": ["config.js" ] + JS_EXTENSION,
     },

    "mirosubs-statwidget":{
        "type": "js",
        "closure_deps": "closure-stat-dependencies.js",
        "include_flash_deps": False,
        "files": [
            'mirosubs.js',
            'rpc.js',
            'loadingdom.js',
            'statwidget/statwidgetconfig.js',
            'statwidget/statwidget.js'],
     },

    "mirosubs-api":{
        "type": "js",
        "files": ["config.js"] + JS_API,
     },
}
