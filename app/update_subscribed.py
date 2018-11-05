from bs4 import BeautifulSoup
from tools import db_utils
import json
from app import app_request

def get_count_from_json(site, response):
    site_name = site.name.encode('ascii')
    if site_name == 'Medium':
        prefix = '])}while(1);</x>'
        response_json = json.loads(response.replace(prefix, ''))
        return response_json['payload']['collection']['metadata']['followerCount']

def is_html(resp):
    if resp is None:
        return False
    content_type = resp.headers['content-type']

    return (resp.status_code == 200 and 'html' in content_type)

def parse_html(url, response):
    if response is None:
        print "No html for " + url
        return ''
    else:
        return BeautifulSoup(response, 'html.parser')

def get_html(site):
    raw_html = app_request.simple_get(site.url.encode("ascii"))
    if raw_html is not None:
        print("....Converting raw html to a BeautifulSoup")
        return BeautifulSoup(raw_html, 'html.parser')
    else:
        return ''

def count_without_text(string):
    return int(filter(str.isdigit, string))

def get_count_from_html(site, html):
    try:
        selector = site.selector.encode("ascii")
        select = html.select(selector)[0]
        count_with_text = select.text.encode("ascii")
        return count_without_text(count_with_text)

    except Exception as e:
        print("Error fetching follower count for", site.name.encode("ascii"))
        return 0


def update_subscribed(platform):
    with db_utils.request_context():
        html = get_html(platform)
        return get_count_from_html(platform, html)
