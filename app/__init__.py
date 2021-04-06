import urllib.parse
from flask import Flask
from flask_babel import Babel

from config import constants

class OriginWeb(Flask):
    def get_send_file_max_age(self, name):
        if name.startswith('js/') or name.startswith('css/'):
            return 0
        return super(OriginWeb, self).get_send_file_max_age(name)

app = OriginWeb(__name__,
    template_folder=constants.TEMPLATE_ROOT,
    static_folder=constants.STATIC_ROOT)

# `.encode('utf8')` will not be needed for python 3
app.jinja_env.filters['quote_plus'] = lambda u: urllib.parse.quote(u.encode('utf8'))
