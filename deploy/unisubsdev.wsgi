import site
site.addsitedir('/var/www/universalsubtitles.dev/env/lib/python2.6/site-packages')

import sys
sys.path.append('/var/www/universalsubtitles.dev')
sys.path.append('/var/www/universalsubtitles.dev/mirosubs')
sys.path.append('/var/www/universalsubtitles.dev/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.unisubsdev-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
