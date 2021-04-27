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
IOS_URL = 'https://itunes.apple.com/app/origin-wallet/id1446091928'
ANDROID_URL = 'https://play.google.com/store/apps/details?id=com.origincatcher'
APK_URL = '/static/files/origin-marketplace-0.23.16.apk'
DAPP_URL = 'https://www.shoporigin.com'
LUPE_URL = 'https://nft.lupefiasco.com'
REWARDS_URL = 'https://www.shoporigin.com/#/welcome'
FAUCET_URL = 'https://faucet.originprotocol.com'

DEFAULT_SHARE_MSG = urllib.parse.quote('Check out ' + BUSINESS_NAME + ', an exciting blockchain project that will decentralize the sharing economy.')
DEFAULT_PARTICLE_ICON = constants.DEFAULT_PARTICLE_ICON

CHROME_EXTENSION_URL = constants.CHROME_EXTENSION_URL
FIREFOX_EXTENSION_URL = constants.FIREFOX_EXTENSION_URL
DSHOP_DEMO_FORM = constants.DSHOP_DEMO_FORM

STAKE_URL = constants.STAKE_URL
