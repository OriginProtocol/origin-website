from app import app_request
from bs4 import BeautifulSoup
import re

sites = []

########### Not working

# sites.append({
#     'name': 'medium',
#     'url': 'https://medium.com/originprotocol',
#     'selector': 'div.u-paddingBottom15',
# })

# sites.append({
#     'name': 'instagram',
#     'url': 'https://www.instagram.com/originprotocol/',
#     'selector': 'span.g47SY',
#     'sub_selector': 'title',
# })


######## Working

sites.append({
    'name': 'youtube',
    'url': 'https://www.youtube.com/c/originprotocol',
    'selector': 'span.subscribed',
})


sites.append({
    'name': 'reddit',
    'url': 'https://old.reddit.com/r/originprotocol/',
    'selector': 'span.number',
})

sites.append({
    'name': 'twitter',
    'url': 'https://twitter.com/originprotocol/',
    'href': '/originprotocol/followers',
    'selector': 'ProfileNav-value',
    'sub_selector': 'data-count',
})

sites.append({
    'name': 'facebook',
    'url': 'https://www.facebook.com/originprotocol',
    'selector': 'clearfix _ikh',
    'sub_selector': 'div._4bl9 div',
})

def facebook_user_count(site, html):
    follower_section = html.find(class_=site['selector'])
    count_section = follower_section.find(class_='_4bl9')
    count_with_text = count_section.div.text.encode("ascii")
    count = int(filter(str.isdigit, count_with_text))
    site['count'] = count

def instagram_user_count(site, html):
    follower_section = html.find(class_=site['selector'])
    count = follower_section['title']
    site['count'] = count.text.encode("ascii")

def twitter_user_count(site, html):
    follower_section = html.find(href=site['href'])
    count = follower_section.find(class_=site['selector'])[site['sub_selector']]
    site['count'] = count.encode("ascii")

def user_count(site, html):
    select = html.select(site['selector'])[0]
    subscribed = select.text.encode("ascii")
    site['count'] = subscribed

def get_html(site):
    raw_html = app_request.simple_get(site['url'])

    if raw_html is not None:
        return BeautifulSoup(raw_html, 'html.parser')
    else:
        return ''

for site in sites:
    html = get_html(site)

    if site['name'] is 'twitter':
        twitter_user_count(site, html)
    elif site['name'] is 'instagram':
        instagram_user_count(site, html)
    elif site['name'] is 'facebook':
        facebook_user_count(site, html)
    else:
        user_count(site, html)
    print(sites)
