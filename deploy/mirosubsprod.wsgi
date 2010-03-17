import site
site.addsitedir('/var/www/universalsubtitles/env/lib/python2.6/site-packages')

import sys
sys.path.append('/var/www/universalsubtitles')
sys.path.append('/var/www/universalsubtitles/mirosubs')
sys.path.append('/var/www/universalsubtitles/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.prod-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
