import os

DEBUG = False

HOST = None
HTTPS = True

PROJECTPATH = os.environ.get('PROJECTPATH')

FLASK_SECRET_KEY = None

APP_LOG_FILENAME = os.path.join(PROJECTPATH, 'app.log')

# SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/dataspaces'

TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

try:
    from constants_override import *
except ImportError:
    pass
