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

YOUTUBE_CHANNEL_ID = dotenv.get('YOUTUBE_CHANNEL_ID')
YOUTUBE_URL = dotenv.get('YOUTUBE_URL')
YOUTUBE_CLIENT_ID = dotenv.get('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = dotenv.get('YOUTUBE_CLIENT_SECRET')
YOUTUBE_PROJECT_ID = dotenv.get('YOUTUBE_PROJECT_ID')
YOUTUBE_REDIRECT_URL = dotenv.get('YOUTUBE_REDIRECT_URL')
YOUTUBE_TOKEN = dotenv.get('YOUTUBE_TOKEN')
YOUTUBE_REFRESH_TOKEN = dotenv.get('YOUTUBE_REFRESH_TOKEN')

DISCORD_BOT_TOKEN = dotenv.get('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = dotenv.get('DISCORD_GUILD_ID')

ETHERSCAN_KEY = dotenv.get('ETHERSCAN_KEY')
AMBERDATA_KEY = dotenv.get('AMBERDATA_KEY')
ETHPLORER_KEY = dotenv.get('ETHPLORER_KEY')

STAKE_URL = dotenv.get('STAKE_URL')

APK_URL = dotenv.get('APK_URL')

FIREFOX_EXTENSION_URL = dotenv.get('FIREFOX_EXTENSION_URL')
CHROME_EXTENSION_URL = dotenv.get('CHROME_EXTENSION_URL')
DSHOP_DEMO_FORM = dotenv.get('DSHOP_DEMO_FORM')

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
