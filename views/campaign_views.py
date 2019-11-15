import os.path
import json
from flask import url_for, render_template

from app import app

MAX_FILE_SIZE = 1024*20  # 20KB
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


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
    conf_file = os.path.join(ROOT, 'partnerconf', '%s.json' % code)

    if not os.path.isfile(conf_file):
        return None

    config_string = ""

    with open(conf_file) as fil:
        config_string = fil.read(MAX_FILE_SIZE)

    if not config_string:
        return None

    config = None
    try:
        config = json.loads(config_string)
    except Exception:
        pass
    return config


@app.context_processor
def campaign_context():
    """ template context processors """
    def url(req, **kwargs):
        """ Add a function url() to make building URLs for views easier """
        if req.url_rule.endpoint:
            endpoint = req.url_rule.endpoint
        elif req.path != '/':
            endpoint = req.path
        else:
            endpoint = 'index'

        view_args = {}
        view_args.update(req.view_args)
        view_args.update(kwargs)

        return url_for(endpoint, **view_args)
    return {'url': url}


@app.route('/partner/<partner_code>', strict_slashes=False)
@app.route('/<lang_code>/partner/<partner_code>', strict_slashes=False)
def partner(partner_code):
    """ Display partner onboarding page directing users to mobile download """

    if not partner_code:
        print 'no code'
        return generic_response(404)

    conf = load_campaign(partner_code)

    if not conf:
        print 'no config'
        return generic_response(404)

    return render_template(
        'partner_campaign.html',
        **conf
    )
