"""
WSGI config for MocketPlace project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from MocketPlace.payments.flask.app import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

django_app = get_wsgi_application()

application = DispatcherMiddleware(django_app, {
    '/flask': flask
})
