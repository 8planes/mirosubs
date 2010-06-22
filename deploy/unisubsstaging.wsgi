import site
site.addsitedir('/var/www/universalsubtitles.staging/env/lib/python2.6/site-packages')

import sys
sys.path.append('/var/www/universalsubtitles.staging')
sys.path.append('/var/www/universalsubtitles.staging/mirosubs')
sys.path.append('/var/www/universalsubtitles.staging/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.unisubsstaging-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
