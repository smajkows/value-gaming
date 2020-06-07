"""
WSGI config for moon_landing_3 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from google.cloud import ndb
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moon_landing_3.settings')

client = ndb.Client()


def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


application = ndb_wsgi_middleware(get_wsgi_application())  # wraps the app in datastore client context
