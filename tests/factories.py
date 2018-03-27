from factory import alchemy, Faker

from database import db
from database.db_models import Interest, Presale, EmailList


class PresaleFactory(alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        model = Presale
        sqlalchemy_session = db.session  # the SQLAlchemy session object

    full_name = Faker('name')
    email = Faker('safe_email')
    accredited = True
    entity_type = 'Individual'
    desired_allocation = '30000'
    desired_allocation_currency = "USD"
    citizenship = "US"
    sending_addr = "0x0000000000000000000000000000000000000000"
    note = Faker('sentence', nb_words=8)
    ip_addr = Faker('ipv4')


class InterestFactory(alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        model = Interest
        sqlalchemy_session = db.session  # the SQLAlchemy session object

    name = Faker('name')
    company_name = Faker('company')
    email = Faker('safe_email')
    website = Faker('domain_name')
    note = Faker('sentence', nb_words=8)


class EmailListFactory(alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        model = EmailList
        sqlalchemy_session = db.session  # the SQLAlchemy session object

    email = Faker('safe_email')
    unsubscribed = False
