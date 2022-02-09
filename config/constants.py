#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv() or load_dotenv('.env')

DEV_EMAIL = os.environ.get('DEV_EMAIL', default=None)

DEBUG = os.environ.get('DEBUG', default=False)

HOST = os.environ.get('HOST')
HTTPS = os.environ.get('HTTPS') in ('True', 'true')

# set the root directory
if (os.path.exists('/etc/heroku')):
    PROJECTPATH = os.environ.get('HOME')
else:
    PROJECTPATH = os.environ.get('PROJECTPATH') or os.getcwd()

DEFAULT_PARTICLE_ICON = os.environ.get('DEFAULT_PARTICLE_ICON')
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

APP_LOG_FILENAME = os.path.join(PROJECTPATH, 'app.log')

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
# SQLAlchemy does not like postgres://
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

FULLCONTACT_KEY = os.environ.get('FULLCONTACT_KEY')

TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SIZE = os.environ.get('RECAPTCHA_SIZE', default="invisible")

SENTRY_DSN = os.environ.get('SENTRY_DSN')

GITHUB_KEY = os.environ.get('GITHUB_KEY')

YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID')
YOUTUBE_URL = os.environ.get('YOUTUBE_URL')
YOUTUBE_CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
YOUTUBE_PROJECT_ID = os.environ.get('YOUTUBE_PROJECT_ID')
YOUTUBE_REDIRECT_URL = os.environ.get('YOUTUBE_REDIRECT_URL')
YOUTUBE_TOKEN = os.environ.get('YOUTUBE_TOKEN')
YOUTUBE_REFRESH_TOKEN = os.environ.get('YOUTUBE_REFRESH_TOKEN')

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = os.environ.get('DISCORD_GUILD_ID')

ETHERSCAN_KEY = os.environ.get('ETHERSCAN_KEY')
AMBERDATA_KEY = os.environ.get('AMBERDATA_KEY')
ETHPLORER_KEY = os.environ.get('ETHPLORER_KEY')

STAKE_URL = os.environ.get('STAKE_URL')

APK_URL = os.environ.get('APK_URL')

FIREFOX_EXTENSION_URL = os.environ.get('FIREFOX_EXTENSION_URL')
CHROME_EXTENSION_URL = os.environ.get('CHROME_EXTENSION_URL')

LAUNCHPAD_API = os.environ.get('LAUNCHPAD_API')

# Language option constants

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
    'vi',
    'id'
]

BINANCE_LOCALE_MAP = {
    'ar': 'en',
    'de': 'de',
    'en': 'en',
    'es': 'es',
    'fr': 'fr',
    'fil': 'en',
    'it': 'it',
    'ja': 'en',
    'ko': 'kr',
    'pt': 'pt',
    'ru': 'ru',
    'th': 'tw',
    'tr': 'tr',
    'zh_Hans': 'cn',
    'zh_Hant': 'cn',
    'el': 'en',
    'he': 'en',
    'hr': 'en',
    'nl': 'nl',
    'vi': 'vn',
    'id': 'en',
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
#     'zh_Hant': 'Chinese (Traditional)'
#     'el': u'Greek',
#     'he': u'Hebrew'
#     'hr': u'Croatian'
#     'nl': u'Dutch'
# }
