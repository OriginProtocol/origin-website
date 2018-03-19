from flask import Flask
from flask_babel import Babel
from flask_assets import Environment, Bundle

import urllib

from config import constants


class MyFlask(Flask):
    def get_send_file_max_age(self, name):
        if name.startswith('js/') or name.startswith('css/'):
            return 0
        return super(MyFlask, self).get_send_file_max_age(name)

app = MyFlask(__name__,
              template_folder=constants.TEMPLATE_ROOT,
              static_folder=constants.STATIC_ROOT)

assets = Environment(app)

js_all = Bundle("js/vendor-jquery-3.2.1.min.js",
                "js/vendor-popper.min.js",
                "js/vendor-bootstrap.min.js",
                "js/alertify.js",
                "js/script.js",
                "js/wow.min.js",
                filters=['jsmin', ],
                output='gen/packed.js')

css_all = Bundle("css/vendor-bootstrap-4.0.0-beta2.css",
                 "css/style.css",
                 "css/alertify.css",
                 "css/animate.css",
                 filters='cssmin',
                 output='gen/packed.css')

assets.register('js_all', js_all)
assets.register('css_all', css_all)

app.jinja_env.filters['quote_plus'] = lambda u: urllib.quote_plus(u.encode('utf8'))
