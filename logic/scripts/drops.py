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
from datetime import date, datetime, timezone, timedelta
from dateutil import parser

fetch_interval_in_minutes = 30
last_fetch = datetime(1900, 1, 1) # A long time ago - to ensure first fetch
cached_drops = []

def sort_drops(drops):
    sorted_drops = sorted(drops, key=lambda x: x.startDate, reverse=True)
    return sorted_drops

def parse_date(date):
    return parser.parse(date)

def filter_upcoming_drops(drops):
    upcomingDrops = []
    for drop in drops:
        if not drop.startDate or not drop.endDate:
            continue
        if (parse_date(drop.startDate) > datetime.now(timezone.utc) or parse_date(drop.endDate) > datetime.now(timezone.utc)):
            drop.countdown = parse_date(drop.startDate).strftime('%A %B %m')
            upcomingDrops.append(drop)
    upcomingDrops = sort_drops(upcomingDrops) 
    
    return upcomingDrops      

def filter_past_drops(drops, allPast):
    pastDrops = []
    for drop in drops:
        if not drop.endDate:
            continue
        if parse_date(drop.endDate) < datetime.now(timezone.utc):
            pastDrops.append(drop) 
    pastDrops = sort_drops(pastDrops)

    if allPast:
        return pastDrops
    else:    
        return pastDrops[slice(0, 3)]  
               

def get_drops(allPast):
    global cached_drops
    global last_fetch
    drops = []
    next_fetch = last_fetch + timedelta(minutes=fetch_interval_in_minutes)

    if datetime.utcnow() < next_fetch:
        drops = cached_drops
    else:
        url = "{0}/site-marketing".format(constants.LAUNCHPAD_API)
        drops = []
        try:
            with closing(requests.get(url)) as resp:
                if resp.status_code == 200:
                    drops = json.loads(resp.content, object_hook=lambda d: SimpleNamespace(**d))
                    last_fetch = datetime.utcnow()
                    cached_drops = drops
                else:
                    return None

        except RequestException as e:
            print("Error during requests to {0} : {1}".format(url, str(e)))
            return None 
  
    upcomingDrops = filter_upcoming_drops(drops)
    pastDrops = filter_past_drops(drops, allPast)    
    return [upcomingDrops, pastDrops, allPast]
