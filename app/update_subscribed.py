from app import app_request
from bs4 import BeautifulSoup

sites = []

sites.append({
    'name': 'youtube',
    'url': 'https://www.youtube.com/c/originprotocol',
    'selector': 'span.subscribed',
})

def user_count(site, html):
    for i, span in enumerate(html.select(site['selector'])):
        subscribed = html.select(site['selector'])[0].text.encode("ascii")
        site['count'] = subscribed
        #save count to database
        #should just count be saved? Or name, url & selector as well
        print(site)
        return True

def get_html(site):
    raw_html = app_request.simple_get(site['url'])
    return BeautifulSoup(raw_html, 'html.parser')

for site in sites:
    html = get_html(site)
    user_count(site, html)
    print(sites)
