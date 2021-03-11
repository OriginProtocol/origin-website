# test_app.py
import pytest
import random
from faker import Faker

from flask import url_for

from config.constants import LANGUAGES
from database.db_models import EmailList, Presale, Interest

from .factories import PresaleFactory, InterestFactory


fake = Faker()


def test_root_returns_200(client):
    res = client.get(url_for('root'))
    assert res.status_code == 200


def test_root_with_lang(client):
    """ Make sure the correct language is returned with lang_code query param """
    res = client.get(url_for('root', lang_code='es'))
    assert res.status_code == 200
    assert '<html lang="es"' in res.get_data()


def test_old_urls(client):
    """ Make sure the old style URLs load properly (e.g. /team) """
    res = client.get(url_for('team', lang_code='en'))
    assert res.status_code == 200
    assert 'Our world-class team is led by entrepreneurs and engineers' in res.get_data()


def test_index_returns_200(client):
    res = client.get(url_for('index', lang_code=random.choice(LANGUAGES)))
    assert res.status_code == 200


def test_join_mailing_and_unsubscribe(mock_send_message, session, client):
    data = {
        "email": fake.safe_email(),
        "ip_addr": fake.ipv4(),
    }
    res = client.post(url_for('join_mailing_list'),
                      data=data)

    assert res.status_code == 200
    assert EmailList.query.filter_by(email=data['email']).first() is not None

    # try to unsubscribe the created EmailList object above
    res = client.get("{url}?email={param}".
                     format(url=url_for('unsubscribe'),
                            param=data['email']))

    assert res.status_code == 302
    assert EmailList.query.filter_by(email=data['email'],
                                     unsubscribed=True).first() is not None


def test_join_presale(mock_send_message, mock_captcha, session, client):
    data = PresaleFactory.stub().__dict__
    data['confirm'] = True

    res = client.post(url_for('join_presale'), data=data)
    created_obj = Presale.query.filter_by(email=data['email']).first()

    assert created_obj.id is not None
    assert res.status_code == 200


@pytest.mark.skip(reason='Route deprecated. Re-enable this test if route gets re-activated')
def test_partners_interest(mock_send_message, mock_captcha, session, client):
    data = InterestFactory.stub().__dict__
    data['confirm'] = True

    res = client.post(url_for('partners_interest'), data=data)
    created_obj = Interest.query.filter_by(email=data['email']).first()

    assert created_obj.id is not None
    assert res.status_code == 200
