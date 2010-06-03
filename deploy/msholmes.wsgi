import site
site.addsitedir('/home/msholmes/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/msholmes')
sys.path.append('/home/msholmes/mirosubs')
sys.path.append('/home/msholmes/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.msholmes-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
