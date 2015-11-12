from app import app
from app import app_config

from views import service_views
from views import web_views

# Silence pyflakes
assert service_views
assert web_views

app_config.init_prod_app(app)

if __name__ == '__main__':
    app.debug = True
    app.run()
