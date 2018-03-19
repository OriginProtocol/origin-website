import logging

from config import constants
from database import db

class AppConfig(object):
    SECRET_KEY = constants.FLASK_SECRET_KEY
    CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = constants.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    RECAPTCHA_SITE_KEY = constants.RECAPTCHA_SITE_KEY
    RECAPTCHA_SECRET_KEY = constants.RECAPTCHA_SECRET_KEY
    RECAPTCHA_SIZE = constants.RECAPTCHA_SIZE


def init_app(app):
    db.init_app(app)


def init_prod_app(app):
    app.config.from_object(__name__ + '.AppConfig')
    init_app(app)

    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [in %(pathname)s:%(lineno)d]: %(message)s')
    if not constants.DEBUG:
        file_handler = logging.FileHandler(constants.APP_LOG_FILENAME)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(log_formatter)
        app.logger.addHandler(file_handler)
    return app
