import site
site.addsitedir('/home/mirosubsdev/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/mirosubsdev')
sys.path.append('/home/mirosubsdev/mirosubs')
sys.path.append('/home/mirosubsdev/mirosubs/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mirosubs.dev-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
