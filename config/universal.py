import urllib.parse

from . import constants

BASE_URL = 'https://' + constants.HOST if constants.HTTPS else 'http://' + constants.HOST

BUSINESS_NAME = 'Origin Protocol'
CONTACT_EMAIL = 'info@originprotocol.com'

WHITEPAPER_URL = BASE_URL + '/whitepaper-v2'

GITHUB_URL = 'https://github.com/originprotocol'
DOCS_URL = 'https://docs.originprotocol.com'
JOBS_URL = 'https://angel.co/originprotocol/jobs'
MEETUP_URL = 'https://www.eventbrite.com/o/origin-protocol-17702006678'
SLACK_URL = 'https://slack.originprotocol.com/'
DISCORD_URL = 'https://discord.gg/jyxpUSe'
TELEGRAM_URL = 'https://t.me/originprotocol'
TELEGRAM_KOREA_URL = 'https://t.me/originprotocolkorea'
VK_URL = 'https://vk.com/originprotocol'
TWITTER_URL = 'https://twitter.com/originprotocol'
FACEBOOK_URL = 'https://www.facebook.com/originprotocol'

STAKE_URL = constants.STAKE_URL
