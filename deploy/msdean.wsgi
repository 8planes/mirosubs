import site
site.addsitedir('/home/msdean/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/msdean')
sys.path.append('/home/msdean/mirosubs')
sys.path.append('/home/msdean/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.msdean-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
