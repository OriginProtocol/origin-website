import os
import re
import json
import requests
from datetime import datetime, timedelta
from flask import (render_template, redirect)

from app import app
from config import universal

MAX_FILE_SIZE = 1024*20  # 20KB
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CACHED_CONFIG = None
CONFIG_CACHE_TIME = None
CACHE_DURATION = timedelta(minutes=5)
IPFS_URL = os.environ.get('IPFS_URL', 'https://ipfs.originprotocol.com/ipfs')
GROWTH_URL = os.environ.get('GROWTH_URL', 'https://growth.originprotocol.com/')
GROWTH_QUERIES = {
    "invite_info": """
        query InviteInfo ($inviteCode: String!) {
          inviteInfo(code: $inviteCode) {
            lastName
            firstName
            avatarURL
          }
        }"""
}


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

        print('conf_file', conf_file)

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


def growth_query(query, vars={}, opName='GenericQuery'):
    """ Run a graphql query against the growth server """
    payload = {
        "operationName": opName,
        "variables": vars,
        "query": query
    }
    print('payload: ', payload)
    resp = requests.post(GROWTH_URL, json=payload, headers={
        'Content-Type': 'application/json'
    })
    print('resp', resp)
    if resp.status_code != 200:
        print('Error querying growth graphql service', resp.text)
        return None
    return resp.json()


def string_or_none(v):
    """ Coax a value to a string """
    if type(v) == str and v != '':
        return v

    try:
        return str(v)
    except ValueError:
        pass

    return None


def ipfs_resolve(url):
    """ Resolve an IPFS URL to an HTTP URL """
    url = string_or_none(url)
    if url is None:
        return ''

    # check for http
    if url.startswith('http://') or url.startswith('https://'):
        print('http url')
        return url

    # check for ifps
    elif url.startswith('ipfs://'):
        match = re.search(r'(Qm[A-Za-z0-9]+)$', url)
        if not match:
            print('invalid url')
            return ''
        try:
            return '%s/%s' % (
                IPFS_URL,
                match.group(1)
            )
        except Exception:
            pass

    # default
    print('default url')
    return ''


@app.route('/partner/<partner_code>', strict_slashes=False)
@app.route('/<lang_code>/partner/<partner_code>', strict_slashes=False)
def partner(partner_code):
    """ Display partner onboarding page directing users to mobile download """

    # Temporarily redirect to welcome page because there are no partner campaigns running currently
    """
    if not partner_code:
        return generic_response(404)

    conf = load_campaign(partner_code)

    if not conf:
        return generic_response(404)

    return render_template(
        'partner_campaign.html',
        referral_code=partner_code,
        app_store_url=universal.IOS_URL,
        play_store_url=universal.ANDROID_URL,
        hide_ogn_banner=True,
        **conf
    )
    """
    return redirect("https://www.originrewards.com", code=302)


@app.route('/referral/<referral_code>', strict_slashes=False)
@app.route('/<lang_code>/referral/<referral_code>', strict_slashes=False)
def referral(referral_code):
    """ Display referral page directing users to mobile download """

    # Temporarily redirect to welcome page because
    """
    if not referral_code:
        return generic_response(404)

    friend_avatar = ''
    friend_name = ''

    response = growth_query(GROWTH_QUERIES.get('invite_info'), {
        'inviteCode': referral_code
    }, 'InviteInfo')

    if response is not None:
        if 'data' in response:
            if 'inviteInfo' in response['data']:
                info = response['data']['inviteInfo']
                print '!!!!info', info
                if type(info) != dict:
                    print 'error - invalid inviteInfo from growth'
                else:
                    friend_name = ('%s %s' % (
                        info.get('firstName'),
                        info.get('lastName')
                    )).strip()
                    friend_avatar = ipfs_resolve(info.get('avatarURL'))

    return render_template(
        'referral_campaign.html',
        referral_code=referral_code,
        app_store_url=universal.IOS_URL,
        play_store_url=universal.ANDROID_URL,
        reward_value=1000,  # TODO: Is this legit?
        friend_name=friend_name,
        hide_ogn_banner=True,
        friend_avatar=friend_avatar or '/static/img/profile-pic-placeholder.svg'
    )
    """
    return redirect("https://www.originrewards.com", code=302)
