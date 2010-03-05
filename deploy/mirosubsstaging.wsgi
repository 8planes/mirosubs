import site
site.addsitedir('/home/mirosubsstaging/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/mirosubsstaging')
sys.path.append('/home/mirosubsstaging/mirosubs')
sys.path.append('/home/mirosubsstaging/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.staging-8planes-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
