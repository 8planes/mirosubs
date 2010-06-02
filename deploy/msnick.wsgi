import site
site.addsitedir('/home/msnick/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/msnick')
sys.path.append('/home/msnick/mirosubs')
sys.path.append('/home/msnick/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.msnick-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
