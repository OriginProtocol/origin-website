import pytest
from .factories import InterestFactory, PresaleFactory, EmailListFactory


@pytest.mark.skip(reason="upgrade made factories and Flask-SQLAlchemy not play nice")
def test_interest_model(session):
    created_obj = InterestFactory.build()
    session.add(created_obj)
    session.commit()

    assert created_obj.id is not None
    assert created_obj.created_at is not None


@pytest.mark.skip(reason="upgrade made factories and Flask-SQLAlchemy not play nice")
def test_presale_model(session):
    created_obj = PresaleFactory.build()
    session.add(created_obj)
    session.commit()

    assert created_obj.id is not None
    assert created_obj.created_at is not None


@pytest.mark.skip(reason="upgrade made factories and Flask-SQLAlchemy not play nice")
def test_email_list_model(session):
    created_obj = EmailListFactory.build()
    session.add(created_obj)
    session.commit()

    assert created_obj.created_at is not None
