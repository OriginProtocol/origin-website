import urllib

import constants

BASE_URL = 'https://' + constants.HOST if constants.HTTPS else 'http://' + constants.HOST

BUSINESS_NAME = 'Origin Protocol'
CONTACT_EMAIL = 'info@originprotocol.com'

PRODUCT_BRIEF_URL = BASE_URL + '/product-brief'
WHITEPAPER_URL = BASE_URL + '/whitepaper'

DEMO_DAPP_URL = 'https://demo.originprotocol.com'

GITHUB_URL = 'https://github.com/originprotocol'
SLACK_URL = 'http://slack.originprotocol.com/'
TELEGRAM_URL = 'https://t.me/originprotocol'
TWITTER_URL = 'https://twitter.com/originprotocol'
FACEBOOK_URL = 'https://www.facebook.com/originprotocol'

DEFAULT_SHARE_MSG = urllib.quote_plus('Check out ' + BUSINESS_NAME + ', an exciting blockchain project that will decentralize the sharing economy.')
