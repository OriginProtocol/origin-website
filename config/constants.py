#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import dotenv

dotenv.load() or dotenv.load('.env')

DEV_EMAIL = dotenv.get('DEV_EMAIL', default=None)

DEBUG = dotenv.get('DEBUG', default=False)

HOST = dotenv.get('HOST')
HTTPS = dotenv.get('HTTPS', default=True)

# set the root directory
if (os.path.exists('/etc/heroku')):
    PROJECTPATH = os.environ.get('HOME')
else:
    PROJECTPATH = os.environ.get('PROJECTPATH') or os.getcwd()

DEFAULT_PARTICLE_ICON = dotenv.get('DEFAULT_PARTICLE_ICON')
FLASK_SECRET_KEY = dotenv.get('FLASK_SECRET_KEY')

APP_LOG_FILENAME = os.path.join(PROJECTPATH, 'app.log')

SQLALCHEMY_DATABASE_URI = dotenv.get('DATABASE_URL')

SENDGRID_API_KEY = dotenv.get('SENDGRID_API_KEY')

FULLCONTACT_KEY = dotenv.get('FULLCONTACT_KEY')

TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

RECAPTCHA_SITE_KEY = dotenv.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = dotenv.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SIZE = dotenv.get('RECAPTCHA_SIZE', default="invisible")

SENTRY_DSN = dotenv.get('SENTRY_DSN')

GITHUB_KEY = dotenv.get('GITHUB_KEY')

# Language option constants

DEFAULT_LANGUAGES = ['en', 'en_US', 'en_GB']

LANGUAGES = [
    'ar',
    'de',
    'en',
    'es',
    'fr',
    'fil',
    'it',
    'ja',
    'ko',
    'pt',
    'ru',
    'th',
    'tr',
    'zh_Hans',
    'zh_Hant',
    'el',
    'he',
    'hr',
    'nl',
    'vi'
]

# LANGUAGES = {
#     'ar': 'Arabic',
#     'de': 'German',
#     'en': 'English',
#     'es': 'Spanish',
#     'fr': 'French',
#     'it': 'Italian',
#     'ja': 'Japanese',
#     'ko': 'Korean',
#     'pt_PT': 'Portugese',
#     'ru': 'Russian',
#     'th': 'Thai',
#     'zh_Hans': 'Chinese (Simplified)',
#     'zh_Hant': 'Chinese (Traditional)'
#     'el': u'Greek',
#     'he': u'Hebrew'
#     'hr': u'Croatian'
#     'nl': u'Dutch'
# }
