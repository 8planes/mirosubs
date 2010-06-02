import site
site.addsitedir('/home/msdennis/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/msdennis')
sys.path.append('/home/msdennis/mirosubs')
sys.path.append('/home/msdennis/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.msdennis-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
