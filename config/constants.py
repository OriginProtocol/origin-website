#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import dotenv

dotenv.load() or dotenv.load('.env')

DEV_EMAIL = dotenv.get('DEV_EMAIL', default=None)

DEBUG = dotenv.get('DEBUG', default=False)

HOST = dotenv.get('HOST')
HTTPS = dotenv.get('HTTPS', default=True)

PROJECTPATH = dotenv.get('PROJECTPATH')

FLASK_SECRET_KEY = dotenv.get('FLASK_SECRET_KEY')

APP_LOG_FILENAME = os.path.join(PROJECTPATH, 'app.log')

SQLALCHEMY_DATABASE_URI = dotenv.get('DATABASE_URL')

SENDGRID_API_KEY = dotenv.get('SENDGRID_API_KEY')

FULLCONTACT_KEY = dotenv.get('FULLCONTACT_KEY')

TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

# Language option constants

LANGUAGES = {
    'ar': u'اللغة العربية',
    'de': u'Deutsch',
    'en': u'English',
    'es': u'Español',
    'fr': u'Français',
    'it': u'Italiano',
    'ja': u'日本語',
    'ko': u'한국어',
    'pt_PT': u'Português',
    'ru': u'Русский',
    'th': u'ไทย',
    'zh_Hans': u'简体中文',
    'zh_TW': u'繁體中文',
    'el': u'Ελληνικά',
    'he': u'עברית‬'
}

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
#     'zh_TW': 'Chinese (Traditional)'
#     'el': u'Hebrew',
#     'iw': u'Greek'
# }
