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

API_ENDPOINT = "http://localhost:3000/api"

def sort_drops(drops):
    sorted_drops = sorted(drops, key=lambda x: x.startDate, reverse=True)
    return sorted_drops

def parse_date(date):
    return parser.parse(date)

def get_countdown(drop):
    current = datetime.now(timezone.utc)
    upcoming = parser.parse(drop.startDate)
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
    return countdown

def filter_upcoming_drops(drops):
    upcomingDrops = []
    for drop in drops:
        if not drop.startDate or not drop.endDate:
            continue
        if (parse_date(drop.startDate) > datetime.now(timezone.utc) or parse_date(drop.endDate) > datetime.now(timezone.utc)):
            drop.countdown = get_countdown(drop)
            upcomingDrops.append(drop)
    upcomingDrops = sort_drops(upcomingDrops) 
    
    page = 1 
    return upcomingDrops[slice(0, 2*page)]       

def filter_past_drops(drops, allPast):
    pastDrops = []
    for drop in drops:
        if not drop.endDate:
            continue
        if parse_date(drop.endDate) < datetime.now(timezone.utc):
            pastDrops.append(drop) 
    pastDrops = sort_drops(pastDrops)

    if allPast == 'true':
        return pastDrops
    else:    
        return pastDrops[slice(0, 3)]  
               

def get_drops(allPast):

    headers = {
    "Content-Type": "application/json",
    }
    url = "{0}/site-marketing".format(API_ENDPOINT)

    drops = []
    try:
        with closing(requests.get(url, headers=headers)) as resp:
            if resp.status_code == 200:
                drops =json.loads(resp.content, object_hook=lambda d: SimpleNamespace(**d))
            else:
                return None

    except RequestException as e:
        print("Error during requests to {0} : {1}".format(url, str(e)))
        return None

    upcomingDrops = filter_upcoming_drops(drops)
    pastDrops = filter_past_drops(drops, allPast)

    return [upcomingDrops, pastDrops]
