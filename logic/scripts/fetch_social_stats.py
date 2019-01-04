from contextlib import closing
import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from database import db, db_models
import requests
from requests.exceptions import RequestException
from sqlalchemy.exc import IntegrityError
from tools import db_utils
from util import tasks

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

steemit_headers = {
    'authority': 'api.steemit.com',
    'method': 'POST',
    'path': '/',
    'scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'referer': 'https://steemit.com/@originprotocol',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}
steemit_data = {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['follow_api', 'get_followers', ['originprotocol', '', 'blog', 1000]],
}

sites = []

sites.append({
    'name': 'Steemit',
    'url': 'https://steemit.com/@originprotocol',
    'selector': '.UserProfile__stats a',
    'json': False
})
sites.append({
    'name': 'Twitter',
    'url': 'https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=originprotocol',
    'json': True
})
sites.append({
    'name': 'Telegram',
    'url': 'http://t.me/originprotocol',
    'selector': 'div.tgme_page_extra',
    'json': False
})
sites.append({
    'name': 'Telegram (Korean)',
    'url': 'https://t.me/originprotocolkorea',
    'selector': 'div.tgme_page_extra',
    'json': False
})
sites.append({
    'name': 'Reddit',
    'url': 'https://old.reddit.com/r/originprotocol/',
    'selector': 'span.number',
    'json': False
})
sites.append({
    'name': 'Facebook',
    'url': 'https://www.facebook.com/originprotocol',
    'selector': '.clearfix ._ikh div._4bl9',
    'json': False
})
sites.append({
    'name': 'Youtube',
    'url': 'https://www.youtube.com/c/originprotocol',
    'selector': 'span.subscribed',
    'json': False
})
sites.append({
    'name': 'Naver',
    'url': 'https://section.blog.naver.com/connect/ViewMoreFollowers.nhn?blogId=originprotocol&widgetSeq=1',
    'selector': 'div.bg_main > div.container > div > div.content_box > div > div > p > strong',
    'json': False
})
sites.append({
    'name': 'KaKao plus friends',
    'url': 'https://pf.kakao.com/_qTxeYC',
    'selector': 'span.num_count',
    'json': False
})
sites.append({
    'name': 'Tencent/QQ video',
    'url': 'http://v.qq.com/vplus/c2564ca8e81c0debabe3c6c6aff3832c',
    'selector': '.user_count_play span.count_num',
    'json': False
})
sites.append({
    'name': 'Youku',
    'url': 'http://i.youku.com/originprotocol',
    'selector': 'div.user-state > ul > li.vnum em',
    'json': False
})
sites.append({
    'name': 'Weibo',
    'url': 'https://www.weibo.com/p/1005056598839228/home?from=page_100505&mod=data&is_hot=1#place',
    'selector': '#Pl_Core_T8CustomTriColumn__3 > div > div > div > table > tbody > tr > td:nth-of-type(2) > a > strong',
    'json': False
})
sites.append({
    'name': 'Medium',
    'url': 'https://medium.com/originprotocol?format=json',
    'json': True,
})

def is_html(resp):
    if resp is None:
        return False
    content_type = resp.headers['content-type']

    return (resp.status_code == 200 and 'html' in content_type)

def get_steemit_content(url):
    try:
        with closing(requests.post(url, headers=steemit_headers, data=json.dumps(steemit_data))) as resp:
            if resp.status_code == 200:
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def get_content(url, use_selenuium = False):
    if use_selenuium is True:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        time.sleep(10)

        return browser.page_source
    else:
        try:
            with closing(requests.get(url, headers=headers, stream=True)) as resp:
                if resp.status_code == 200:
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

def count_without_text(string):
    # need to handle if there are no numbers
    return int(filter(str.isdigit, string))

def get_count_from_html(site, html):
    try:
        selector = site['selector'].encode("ascii")
        select = html.select(selector)[0]
        count_with_text = select.text.encode("ascii")
        return count_without_text(count_with_text)

    except Exception as e:
        message = "Error fetching follower count for", site['name'].encode("ascii")
        print(message)

        return { 'error': message }

def get_count_from_json(site, content):
    site_name = site['name'].encode('ascii')
    if site_name == 'Twitter':
        content_json = json.loads(content)
        return content_json[0]['followers_count']
    if site_name == 'Medium':
        prefix = '])}while(1);</x>'
        content_json = json.loads(content.replace(prefix, ''))
        return content_json['payload']['collection']['metadata']['followerCount']
    if site_name == 'Steemit':
        content_json = json.loads(content)
        followers = [d['follower'] for d in content_json['result'] if 'follower' in d]
        return len(followers)

def update_subscribed(site):
    url = site['url'].encode('ascii')
    site_name = site['name'].encode('ascii')

    if site_name == 'Weibo':
        content = get_content(url, True)
    elif site_name == 'Steemit':
        content = get_steemit_content(url)
    else:
        content = get_content(url)

    try:
        if site['json']:
            return get_count_from_json(site, content)
        else:
            html = BeautifulSoup(content, 'html.parser')
            return get_count_from_html(site, html)
    except Exception as e:
        print(str(e))

def update_subscribed_count():
    for site in sites:
        updated_count = update_subscribed(site)
        if isinstance(updated_count, int):
            print("Updating stats for " + site['name'] + ": " + str(updated_count))
            stat = db_models.SocialStat()
            stat.name = site['name']
            stat.subscribed_count = updated_count
            db.session.add(stat)
    db.session.commit()

with db_utils.request_context():
    update_subscribed_count()
