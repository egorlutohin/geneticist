import os
import sys

#os.environ['DJANGO_SETTINGS_MODULE'] = 'db_gnokdc.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

sys.path.insert(0, '/home/geneticist/www/')
sys.path.insert(0, '/home/geneticist/www/geneticist/')
sys.path.insert(0, '/home/geneticist/www/src/django-history/')
sys.path.insert(0, '/home/geneticist/www/lib/python2.6/site-packages/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
