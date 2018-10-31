import requests
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

headers = {'User-agent': 'Test Bot'}

def simple_get(url):
    try:
        with closing(get(url, headers=headers, stream=True)) as resp:
            if is_html(resp):
                return resp.content
            else:
                print "No html for " + url
                return None

    except RequestException as e:
        error = 'Error during requests to {0} : {1}'.format(url, str(e))
        print(error)
        return None

def is_html(resp):
    if resp is None:
        return False
    content_type = resp.headers['content-type']

    return (resp.status_code == 200 and 'html' in content_type)
