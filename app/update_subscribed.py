from app import app_request
from bs4 import BeautifulSoup
from tools import db_utils

def count_without_text(string):
    return int(filter(str.isdigit, string))

def follower_count(site, html):
    try:
        selector = site.selector.encode("ascii")
        select = html.select(selector)[0]
        count_with_text = select.text.encode("ascii")
        return count_without_text(count_with_text)

    except Exception as e:
        print("Error fetching follower count for", site.name.encode("ascii"))
        return 0

def get_html(site):
    raw_html = app_request.simple_get(site.url.encode("ascii"))
    if raw_html is not None:
        return BeautifulSoup(raw_html, 'html.parser')
    else:
        return ''

def update_subscribed(platform):
    with db_utils.request_context():
        html = get_html(platform)

        return follower_count(platform, html)
