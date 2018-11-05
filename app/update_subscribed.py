from bs4 import BeautifulSoup
from tools import db_utils
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

def get_content(url):
    headers = {'User-agent': 'Test Bot'}

    try:
        with closing(get(url, headers=headers, stream=True)) as resp:
            if resp.status_code == 200:
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def parse_html(url, content):
    if True:
        return BeautifulSoup(content, 'html.parser')
    else:
        print "No html for " + url
        return ''

def count_without_text(string):
    # need to handle if there are no numbers
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

def get_count_from_json(site, content):
    site_name = site.name.encode('ascii')
    if site_name == 'Medium':
        prefix = '])}while(1);</x>'
        content_json = json.loads(content.replace(prefix, ''))
        return content_json['payload']['collection']['metadata']['followerCount']

def update_subscribed(platform):
    with db_utils.request_context():
        url = platform.url.encode('ascii')
        content = get_content(url)

        try:
            if platform.json:
                return get_count_from_json(platform, content)
            else:
                html = BeautifulSoup(content, 'html.parser')
                return get_count_from_html(platform, html)
        except Exception as e:
            print(str(e))
            return 0
