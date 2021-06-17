from contextlib import closing
import json
import webbrowser
import re

from bs4 import BeautifulSoup

import requests
from requests.exceptions import RequestException
from tools import db_utils
from util import tasks
from config import constants
from types import SimpleNamespace
from datetime import date, datetime, timezone
from dateutil import parser



headers = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

sites = []

API_ENDPOINT = "https://origin-nft-api.com"

# def get_drops():
#     headers = {
#         "Content-Type": "application/json",
#     }
#     url = "{0}/drops".format(API_ENDPOINT)

#     try:
#         with closing(requests.get(url, headers=headers)) as resp:
#             if resp.status_code == 200:
#                 return len(json.loads(resp.content))
#             else:
#                 return None

#     except RequestException as e:
#         print("Error during requests to {0} : {1}".format(url, str(e)))
#         return None

def get_start(drop):
    time = parser.parse(drop.start)
    return time

def get_drops():
    drops = json.loads(open('static/files/drops-mock.json').read(), object_hook=lambda d: SimpleNamespace(**d))  
    
    sortedDrops = sorted(
    drops,
    key=lambda x: x.start, reverse=True)

    upcomingDrops = sortedDrops[slice(2)]
    for upcomingDrop in upcomingDrops:
        current = datetime.now(timezone.utc)
        upcoming = parser.parse(upcomingDrop.start)
        difference = (upcoming - current).total_seconds()
        remaining = difference
        
        day = remaining // (24 * 3600)
        remaining = remaining - (day * (24 * 3600))

        time = remaining % (24 * 3600)
        hour = remaining // 3600
        remaining = remaining - (hour * 3600)

        time %= 3600
        minutes = remaining // 60
        countdown = "%dd %dh %dm" % (day, hour, minutes)
        upcomingDrop.countdown = countdown

    pastDrops = sortedDrops[slice(2, len(drops))]

    return [upcomingDrops, pastDrops]
