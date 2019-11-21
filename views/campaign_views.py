import os.path
import json
from datetime import datetime, timedelta
from flask import render_template

from app import app

MAX_FILE_SIZE = 1024*20  # 20KB
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CACHED_CONFIG = None
CONFIG_CACHE_TIME = None
CACHE_DURATION = timedelta(minutes=5)


def generic_response(status_code):
    """ Render a generic response by HTTP status code """
    return (render_template('%s.html' % status_code), status_code)


def load_campaign(code):
    """ Load campaign definitiaon JSON

    Example (../partnerconf/<code>.json):
    {
      "partner": {
        "name": "Samsung",
        "logo": "https://originprotocol.com/images/samsung_logo.png"
      },
      "reward": {
        "value": 1000000000000000000,
        "currency": "ogn"
      },
      "referalCode": "samsung2019abc"
    }
    """
    global CACHED_CONFIG, CONFIG_CACHE_TIME, CACHE_DURATION

    # Load config if it hasn't already or cache is expired
    if CACHED_CONFIG is None or (
        CONFIG_CACHE_TIME is None
        or CONFIG_CACHE_TIME - CACHE_DURATION > datetime.now()
    ):
        conf_file = os.path.join(ROOT, 'static', 'partnerconf', 'campaigns.json')

        print 'conf_file', conf_file

        if not os.path.isfile(conf_file):
            return None

        config_string = ""

        with open(conf_file) as fil:
            config_string = fil.read(MAX_FILE_SIZE)

        if not config_string:
            return None

        CACHED_CONFIG = None
        try:
            CACHED_CONFIG = json.loads(config_string)
        except Exception:
            pass

    return CACHED_CONFIG.get(code)


@app.route('/partner/<partner_code>', strict_slashes=False)
@app.route('/<lang_code>/partner/<partner_code>', strict_slashes=False)
def partner(partner_code):
    """ Display partner onboarding page directing users to mobile download """

    if not partner_code:
        return generic_response(404)

    conf = load_campaign(partner_code)

    if not conf:
        return generic_response(404)

    return render_template(
        'partner_campaign.html',
        referal_code=partner_code,
        **conf
    )
