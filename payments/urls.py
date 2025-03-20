from django.urls import re_path
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from MocketPlace.payments.flask.app import flask
from werkzeug.wsgi import DispatcherMiddleware
from django.core.wsgi import get_wsgi_application

# Create a combined WSGI application
application = DispatcherMiddleware(get_wsgi_application(), {
    '/flask': flask  # all routes under /flask/ go to Flask
})
