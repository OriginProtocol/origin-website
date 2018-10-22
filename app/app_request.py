from requests import get
from requests.exceptions import RequestException
from contextlib import closing

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_html(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        error = 'Error during requests to {0} : {1}'.format(url, str(e))
        print(error)
        return None


def is_html(resp):
    content_type = resp.headers['content-type']

    return (resp.status_code == 200
            and content_type is not None
            and 'html' in content_type)
