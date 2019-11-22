import pytest
from testing.postgresql import Postgresql
from mock import patch

from app import app as flask_app
from database import db as _db
from config import constants

from util.context import create_contexts

# importing to register views
from views import web_views # noqa
from views import campaign_views # noqa


create_contexts(flask_app)


class TestConfig(object):
    SECRET_KEY = constants.FLASK_SECRET_KEY

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    RECAPTCHA_SITE_KEY = constants.RECAPTCHA_SITE_KEY
    RECAPTCHA_SECRET_KEY = constants.RECAPTCHA_SECRET_KEY
    RECAPTCHA_SIZE = constants.RECAPTCHA_SIZE
    SERVER_NAME = 'localhost'


@pytest.yield_fixture(scope='session')
def app():
    _app = flask_app
    _app.config.from_object(__name__ + '.TestConfig')
    with Postgresql() as postgresql:
        _app.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()
        ctx = _app.app_context()
        ctx.push()

        yield _app

        ctx.pop()


@pytest.yield_fixture
def client(app):
    """A Flask test client. An instance of :class:`flask.testing.TestClient`
    by default.
    """
    with app.test_client() as client:
        yield client


@pytest.yield_fixture(scope='session')
def db(app):
    _db.app = app
    _db.init_app(app)
    _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.yield_fixture(scope='function')
def mock_captcha(app):
    patcher = patch('views.web_views.recaptcha', return_value=True)
    yield patcher.start()
    patcher.stop()


@pytest.yield_fixture(scope='function')
def mock_send_message(app):
    patcher = patch('util.sendgrid_wrapper.send_message', return_value=True)
    yield patcher.start()
    patcher.stop()

@pytest.yield_fixture(scope='function')
def mock_subscribe(app):
    patcher = patch('logic.emails.mailing_list.add_sendgrid_contact', return_value=True)
    yield patcher.start()
    patcher.stop()

@pytest.yield_fixture(scope='function')
def mock_subscribe(app):
    patcher = patch('logic.emails.mailing_list.unsubscribe_sendgrid_contact', return_value=True)
    yield patcher.start()
    patcher.stop()