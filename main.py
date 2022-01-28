import os
from app import app
from app import app_config
from config import constants
from util import patches
from util.context import create_contexts

from flask_compress import Compress

from views import web_views
from views import campaign_views

from flask_migrate import Migrate
from database import db

# Silence pyflakes
assert patches
assert web_views
assert campaign_views

# enable gzip since it's not supported out of the box on Heroku
Compress(app)

app_config.init_prod_app(app)

# Template context processors
create_contexts(app)

migrate = Migrate(app, db)

if __name__ == '__main__':

    # speeds up development by auto-restarting the server when templates change
    if constants.DEBUG:
        extra_dirs = ['templates',]
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)
    else:
        extra_files=None

    app.debug = constants.DEBUG
    port = int(os.environ.get("PORT", 5002))
    app.run(
        host='0.0.0.0',
        port=port,
        threaded=True,
        extra_files=extra_files
    )
