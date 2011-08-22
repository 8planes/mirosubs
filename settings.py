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
import os, sys

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

USE_BUNDLED_MEDIA = not DEBUG

COMPRESS_YUI_BINARY = "java -jar ./css-compression/yuicompressor-2.4.6.jar"
COMPRESS_OUTPUT_DIRNAME = "static-cache"


USER_LANGUAGES_COOKIE_NAME = 'unisub-languages-cookie'

# paths provided relative to media/js
JS_CORE = \
    ['js/mirosubs.js', 
     'js/rpc.js',
     'js/clippy.js',
     'js/flash.js',
     'js/spinner.js',
     'js/sliderbase.js',
     'js/closingwindow.js',
     'js/loadingdom.js',
     'js/tracker.js',
     'js/style.js',
     'js/messaging/simplemessage.js',
     'js/video/video.js',
     'js/video/captionview.js',
     'js/video/abstractvideoplayer.js',
     'js/video/flashvideoplayer.js',
     'js/video/html5videoplayer.js',
     'js/video/youtubevideoplayer.js',
     'js/video/ytiframevideoplayer.js',
     'js/video/youtubebasemixin.js',
     'js/video/jwvideoplayer.js',
     'js/video/flvvideoplayer.js',
     'js/video/videosource.js',
     'js/video/html5videosource.js',
     'js/video/youtubevideosource.js',
     'js/video/ytiframevideosource.js',
     'js/video/brightcovevideosource.js',
     'js/video/brightcovevideoplayer.js',
     'js/video/flvvideosource.js',
     'js/video/bliptvplaceholder.js',
     'js/video/controlledvideoplayer.js',
     'js/video/vimeovideosource.js',
     'js/video/vimeovideoplayer.js',
     'js/video/dailymotionvideosource.js',
     'js/video/dailymotionvideoplayer.js',
     'js/startdialog/model.js',
     'js/startdialog/videolanguage.js',
     'js/startdialog/videolanguages.js',
     'js/startdialog/tolanguage.js',
     'js/startdialog/tolanguages.js',
     'js/startdialog/dialog.js',
     'js/requestdialog.js',
     'js/widget/subtitle/editablecaption.js',
     "js/widget/subtitle/editablecaptionset.js",
     'js/widget/usersettings.js',
     'js/widget/logindialog.js',
     'js/widget/videotab.js',
     'js/widget/howtovideopanel.js',
     'js/widget/dialog.js',
     'js/widget/captionmanager.js',
     'js/widget/rightpanel.js',
     'js/widget/basestate.js',
     'js/widget/subtitlestate.js',
     'js/widget/dropdowncontents.js',
     'js/widget/playcontroller.js',
     'js/widget/subtitlecontroller.js',
     'js/widget/subtitledialogopener.js',
     'js/widget/opendialogargs.js',
     'js/widget/dropdown.js',
     'js/widget/play/manager.js',
     'js/widget/widgetcontroller.js',
     'js/widget/widget.js'
]

JS_DIALOG = \
    ['js/subtracker.js',
     'js/srtwriter.js',
     'js/widget/unsavedwarning.js',
     'js/widget/resumeeditingrecord.js',
     'js/widget/droplockdialog.js',
     'js/finishfaildialog/dialog.js',
     'js/finishfaildialog/errorpanel.js',
     'js/finishfaildialog/reattemptuploadpanel.js',
     'js/finishfaildialog/copydialog.js',
     'js/widget/subtitle/dialog.js',
     'js/widget/subtitle/msservermodel.js',
     'js/widget/subtitle/subtitlewidget.js',
     'js/widget/subtitle/addsubtitlewidget.js',
     'js/widget/subtitle/subtitlelist.js',
     'js/widget/subtitle/transcribeentry.js',
     'js/widget/subtitle/transcribepanel.js',
     'js/widget/subtitle/transcriberightpanel.js',
     'js/widget/subtitle/syncpanel.js',
     'js/widget/subtitle/reviewpanel.js',
     'js/widget/subtitle/reviewrightpanel.js',
     'js/widget/subtitle/sharepanel.js',
     'js/widget/subtitle/completeddialog.js',
     'js/widget/subtitle/editpanel.js',
     'js/widget/subtitle/onsaveddialog.js',
     'js/widget/subtitle/editrightpanel.js',
     'js/widget/subtitle/bottomfinishedpanel.js',
     'js/widget/subtitle/logger.js',
     'js/widget/subtitle/savedsubtitles.js',
     'js/widget/timeline/timerow.js',
     'js/widget/timeline/timerowul.js',
     'js/widget/timeline/timelinesub.js',
     'js/widget/timeline/timelinesubs.js',
     'js/widget/timeline/timelineinner.js',
     'js/widget/timeline/timeline.js',
     'js/widget/timeline/subtitle.js',
     'js/widget/timeline/subtitleset.js',
     'js/widget/controls/bufferedbar.js',
     'js/widget/controls/playpause.js',
     'js/widget/controls/progressbar.js',
     'js/widget/controls/progressslider.js',
     'js/widget/controls/timespan.js',
     'js/widget/controls/videocontrols.js',
     'js/widget/controls/volumecontrol.js',
     'js/widget/controls/volumeslider.js',
     'js/widget/translate/googletranslator.js',
     'js/widget/translate/dialog.js',
     'js/widget/translate/translationpanel.js',
     'js/widget/translate/translationlist.js',
     'js/widget/translate/translationwidget.js',
     'js/widget/translate/translationrightpanel.js',
     'js/widget/translate/forkdialog.js',
     'js/widget/translate/titletranslationwidget.js']

JS_OFFSITE = list(JS_CORE)
JS_OFFSITE.append('js/widget/crossdomainembed.js')

JS_ONSITE = list(JS_CORE)
JS_ONSITE.extend(
    ['js/srtwriter.js',
     'js/widget/samedomainembed.js',
     "js/widget/api/servermodel.js",
     "js/widget/api/api.js"])

JS_WIDGETIZER_CORE = list(JS_CORE)
JS_WIDGETIZER_CORE.extend([
    "js/widget/widgetdecorator.js",
    "js/widgetizer/videoplayermaker.js",
    "js/widgetizer/widgetizer.js",
    "js/widgetizer/youtube.js",
    "js/widgetizer/html5.js",
    "js/widgetizer/jwplayer.js",
    "js/widgetizer/youtubeiframe.js"])

JS_WIDGETIZER = list(JS_WIDGETIZER_CORE)
JS_WIDGETIZER.append('js/widgetizer/dowidgetize.js')

JS_EXTENSION = list(JS_WIDGETIZER_CORE)
JS_EXTENSION.append('js/widgetizer/extension.js')

JS_API = list(JS_CORE)
JS_API.extend(JS_DIALOG)
JS_API.extend([
        "js/widget/api/servermodel.js",
        "js/widget/api/api.js"])

JS_BASE_DEPENDENCIES = [
    'js/closure-library/closure/goog/base.js',
    'js/closure-dependencies.js',
    'js/swfobject.js',
    'flowplayer/flowplayer-3.2.2.min.js',
]

JS_MODERATION_DASHBOARD =  [
    "js/jquery-1.4.3.js",
    "js/jquery-ui-1.8.13.custom.min.js",
    "js/jgrowl/jquery.jgrowl.js",
    "js/jalerts/jquery.alerts.js",
    "js/jquery.form.js",
    "js/jquery.metadata.js",
    "js/jquery.mod.js",
    "js/jquery.rpc.js",
    "js/jquery.input_replacement.min.js",
    'js/closure-library/closure/goog/base.js',    
    'js/closure-dependencies.js',    
    "js/messages.js",
    "js/jquery.address-1.4.fixed.js",
    "js/jquery.ajax-paginator.js",
    "js/moderation/simplewarning.js",
    "js/moderation/confirmrejectiondialog.js",
    ]
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
    'context_processors.current_site',
    'context_processors.current_commit',
    'context_processors.custom',
    'context_processors.user_languages',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'utils.context_processors.media',
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
    'doorman',
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
    #re.compile('^/crossdomain.xml'),
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

ANONYMOUS_USER_ID = 10000

#Use on production
GOOGLE_ANALYTICS_NUMBER = 'UA-163840-22'
MIXPANEL_TOKEN = '44205f56e929f08b602ccc9b4605edc3'

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    sys.stderr.write("deploy/create_commit_file must be ran before boostrapping django")
    LAST_COMMIT_GUID = "dev/dev"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DEFAULT_BUCKET = ''
USE_AMAZON_S3 = AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and DEFAULT_BUCKET

AVATAR_MAX_SIZE = 500*1024
THUMBNAILS_SIZE = (
    (100, 100),
    (50, 50),
    (120, 90)
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
     "new_home":{
         "type":"css",
         "files":(
            "css/new_index.css",
             "css/nyroModal.css",
             "css/mirosubs-widget.css",
          ),
         },
    "widget-css":{
         "type":"css",
         "files":(
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
        "closure_deps": "js/closure-dependencies.js",
        "files": ["js/config.js"] + JS_WIDGETIZER,
        "bootloader": { 
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
     },
    "mirosubs-widgetizer-sumo": {
        "type": "js",
        "closure_deps": "js/closure-dependencies.js",
        "files": ["js/config.js"] + JS_WIDGETIZER,
        "extra_defines": {"mirosubs.REPORT_ANALYTICS": "false"},
        "bootloader": { 
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
    },
    "mirosubs-widgetizer-debug": {
        "type": "js",
        "files": ["js/config.js" ] + JS_WIDGETIZER  ,
        "closure_deps": "js/closure-dependencies.js",
        "debug": True,
        "bootloader": { 
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
     },
    "mirosubs-extension":{
        "type": "js",
        "files": ["js/config.js" ] + JS_EXTENSION,
     },
    "mirosubs-statwidget":{
        "type": "js",
        "closure_deps": "js/closure-stat-dependencies.js",
        "include_flash_deps": False,
        "files": [
            'js/mirosubs.js',
            'js/rpc.js',
            'js/loadingdom.js',
            'js/statwidget/statwidgetconfig.js',
            'js/statwidget/statwidget.js'],
     },

    "mirosubs-api":{
        "type": "js",
        "files": ["js/config.js"] + JS_API,
        "bootloader": { 
            "gatekeeper": "UnisubsApiLoaded", 
            "render_bootloader": False
        }
     },
    "js-base-dependencies":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "files": JS_BASE_DEPENDENCIES,
     },
    "js-onsite-dialog": {
        "type":"js",
        "files": ["js/config.js"]  + JS_DIALOG  ,
    },
    "site_base_js":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "files":[
              "js/jquery-1.4.3.js",
              "js/jquery-ui-1.8.13.custom.min.js",
              "js/jgrowl/jquery.jgrowl.js",
              "js/jalerts/jquery.alerts.js",
              "js/jquery.form.js",
              "js/jquery.metadata.js",
              "js/jquery.mod.js",
              "js/jquery.rpc.js",
              "js/jquery.input_replacement.min.js",
              "js/messages.js",

            ],
        "optimizations": "SIMPLE_OPTIMIZATIONS",
        "closure_deps": "",
        "include_flash_deps": False,
        },
    "js-testing-base":{
        "type":"js",
        "files": [
                 'js/widget/testing/stubvideoplayer.js',
                 'js/widget/testing/events.js',
                "js/subtracker.js" ,
                "js/unitofwork.js",
                "js/testing/testing.js",
                "js/testing/timerstub.js",
            ]
    },
    "js-moderation-dashboard":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "closure_deps": "js/closure-dependencies.js",
        "files": JS_MODERATION_DASHBOARD,
    },
    "debug-embed-js": {
        "type": "js",
        "optimizations": "WHITESPACE_ONLY",
        "files": JS_BASE_DEPENDENCIES + JS_OFFSITE[:-1]
    }
}


FEATURE_FLAGS  = {
    "MODERATION": False
}
