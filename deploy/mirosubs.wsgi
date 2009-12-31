import site
site.addsitedir('/home/mirosubs/env/lib/python2.5/site-packages')

import sys
sys.path.append('/home/mirosubs/mirosubs')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.staging-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
