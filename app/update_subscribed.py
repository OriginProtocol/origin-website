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

# sites.append({
#     'name': 'telegram',
#     'url': 'http://t.me/originprotocol',
#     'selector': 'div.tgme_page_extra',
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
    'sub_selector': '_4bl9',
})

def count_without_text(string):
    return int(filter(str.isdigit, string))

def facebook_follower_count(site, html):
    follower_section = html.find(class_=site['selector'])
    count_section = follower_section.find(class_=site['sub_selector'])
    count_with_text = count_section.div.text.encode("ascii")
    count = count_without_text(count_with_text)
    site['count'] = count

def instagram_follower_count(site, html):
    follower_section = html.find(class_=site['selector'])
    count = follower_section['title']
    site['count'] = count.text.encode("ascii")

def twitter_follower_count(site, html):
    follower_section = html.find(href=site['href'])
    count = follower_section.find(class_=site['selector'])[site['sub_selector']]
    site['count'] = count.encode("ascii")

def follower_count(site, html):
    select = html.select(site['selector'])[0]
    subscribed = select.text.encode("ascii")
    site['count'] = count_without_text(subscribed)

def get_html(site):
    raw_html = app_request.simple_get(site['url'])

    if raw_html is not None:
        return BeautifulSoup(raw_html, 'html.parser')
    else:
        return ''

for site in sites:
    html = get_html(site)

    if site['name'] is 'twitter':
        twitter_follower_count(site, html)
    elif site['name'] is 'instagram':
        instagram_follower_count(site, html)
    elif site['name'] is 'facebook':
        facebook_follower_count(site, html)
    else:
        follower_count(site, html)
    print(sites)
