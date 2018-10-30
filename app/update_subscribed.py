from app import app_request
from bs4 import BeautifulSoup
import re

sites = []

########### Not working

# sites.append({
#     'name': 'Medium',
#     'url': 'https://medium.com/originprotocol',
#     'selector': 'div.u-paddingBottom15',
# })

# sites.append({
#     'name': 'Weibo',
#     'url': 'https://m.weibo.cn/u/6598839228',
#     'selector': '.mod-fil-fans .text-shadow:nth-of-type(2)',
# })

####### Working

sites.append({
    'name': 'Telegram',
    'url': 'http://t.me/originprotocol',
    'selector': 'div.tgme_page_extra',
})

sites.append({
    'name': 'Reddit',
    'url': 'https://old.reddit.com/r/originprotocol/',
    'selector': 'span.number',
})

sites.append({
    'name': 'Twitter',
    'url': 'https://twitter.com/originprotocol/',
    'href': '/originprotocol/followers',
    'selector': 'ProfileNav-value',
    'sub_selector': 'data-count',
})

sites.append({
    'name': 'Facebook',
    'url': 'https://www.facebook.com/originprotocol',
    'selector': '.clearfix ._ikh div._4bl9',
})

sites.append({
    'name': 'Youtube',
    'url': 'https://www.youtube.com/c/originprotocol',
    'selector': 'span.subscribed',
})

sites.append({
    'name': 'Naver',
    'url': 'https://section.blog.naver.com/connect/ViewMoreFollowers.nhn?blogId=originprotocol&widgetSeq=1',
    'selector': 'div.bg_main > div.container > div > div.content_box > div > div > p > strong',
})

sites.append({
    'name': 'KaKao plus friends',
    'url': 'https://pf.kakao.com/_qTxeYC',
    'selector': 'span.num_count',
})

sites.append({
    'name': 'Tencent/QQ video',
    'url': 'http://v.qq.com/vplus/c2564ca8e81c0debabe3c6c6aff3832c',
    'selector': '.user_count_play span.count_num',
})

sites.append({
    'name': 'Youku',
    'url': 'http://i.youku.com/originprotocol',
    'selector': 'div.YK-box div.hd > div.title > a > span > font > font',
})

sites.append({
    'name': 'Instagram',
    'url': 'https://www.instagram.com/originprotocol',
    'selector': '.zwlfE .k9GMp',

})

def count_without_text(string):
    return int(filter(str.isdigit, string))

def youku_follower_count(site, html):
    follower_section = html.find(attrs={'module': 'followers'})
    count_section = follower_section.select('div.YK-box .hd .title a span')[0]
    count_with_text = count_section.text.encode("ascii")
    site['count'] = count_without_text(count_with_text)

def facebook_follower_count(site, html):
    follower_section = html.select(site['selector'])[1]
    count_with_text = follower_section.div.text.encode("ascii")
    site['count'] = count_without_text(count_with_text)

def instagram_follower_count(site, html):
    meta_section = html.find(content=re.compile("Follower"))
    content = meta_section['content']
    count = content.split("Followers", 1)[0]
    site['count'] = count.encode("ascii")

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

    if site['name'] is 'Twitter':
        twitter_follower_count(site, html)
    elif site['name'] is 'Instagram':
        instagram_follower_count(site, html)
    elif site['name'] is 'Facebook':
        facebook_follower_count(site, html)
    elif site['name'] is 'Youku':
        youku_follower_count(site, html)
    else:
        follower_count(site, html)

print(sites)
