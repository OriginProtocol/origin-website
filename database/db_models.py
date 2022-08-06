
from decimal import *

from sqlalchemy import event
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from database import db, db_common


class EmailList(db.Model):
    __tablename__ = 'email_list'

    email = db.Column(db.String(255), primary_key=True, autoincrement=False)
    unsubscribed = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    ip_addr = db.Column(db.String(100))
    country_code = db.Column(db.String(2))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    # sendgrid feedback loop
    bounced = db.Column(db.Boolean())
    spam_report = db.Column(db.Boolean())
    blocked = db.Column(db.Boolean())
    invalid = db.Column(db.Boolean())

    def __str__(self):
        return '%s' % (self.email)


class Presale(db.Model):
    __tablename__ = 'presale'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    accredited = db.Column(db.Boolean())
    entity_type = db.Column(db.String(255))
    desired_allocation = db.Column(db.String(255))
    desired_allocation_currency = db.Column(db.String(3))
    citizenship = db.Column(db.String(2))
    sending_addr = db.Column(db.String(255))
    note = db.Column(db.Text())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    ip_addr = db.Column(db.String(100))

    def __str__(self):
        return '%s' % (self.email)


class FullContact(db.Model):
    __tablename__ = 'fullcontact'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    fullcontact_response = db.Column(JSONB)
    github_handle = db.Column(db.String(255))
    angellist_handle = db.Column(db.String(255))
    twitter_handle = db.Column(db.String(255))


class MessageLog(db.Model):
    __tablename__ = 'message_log'

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), index=True)
    msg_purpose = db.Column(db.String(128), index=True)
    msg_subject = db.Column(db.String(128))
    msg_text = db.Column(db.Text())
    msg_html = db.Column(db.Text())
    msg_sent = db.Column(db.DateTime(timezone=True), server_default=db.func.now())


class Interest(db.Model):
    __tablename__ = 'interest'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    note = db.Column(db.Text())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    ip_addr = db.Column(db.String(100))

    def __str__(self):
        return '%s' % (self.email)


class Contributor(db.Model):
    __tablename__ = 'contributor'

    username = db.Column(db.String(255), primary_key=True, autoincrement=False)
    commits = db.Column(db.Integer())
    avatar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __str__(self):
        return '%s' % (self.username)

class SocialStat(db.Model):
    __tablename__ = 'social_stat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    subscribed_count = db.Column(db.Integer())

    def __str__(self):
        return '%s' % (self.name)

class EthContact(db.Model):
    __tablename__ = 'eth_contact'
    address = db.Column(db.String(42), primary_key=True)
    name = db.Column(db.String(255), index=True)
    desc = db.Column(db.String(255))
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(255), index=True)
    eth_balance = db.Column(db.Float(), default=0)
    ogn_balance = db.Column(db.Float(), default=0)
    ogv_balance = db.Column(db.Float(), default=0)
    dai_balance = db.Column(db.Float(), default=0)
    investor = db.Column(db.Boolean())
    presale_interest = db.Column(db.Boolean())
    dapp_user = db.Column(db.Boolean())
    employee = db.Column(db.Boolean())
    exchange = db.Column(db.Boolean())
    company_wallet = db.Column(db.Boolean())
    investor_airdrop = db.Column(db.Boolean())
    token_count = db.Column(db.Integer())
    transaction_count = db.Column(db.Integer())
    tokens = db.Column(JSONB)
    last_updated = db.Column(db.DateTime(),server_default=db.func.now(), onupdate=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    country_code = db.Column(db.String(2))

    def __str__(self):
        return '%s' % (self.name)

class TokenTransaction(db.Model):
    __tablename__ = 'token_transaction'
    tx_hash = db.Column(db.String(66), primary_key=True)
    from_address = db.Column(db.String(42), index=True)
    to_address = db.Column(db.String(42), index=True)
    amount = db.Column(db.Float())
    block_number = db.Column(db.Integer())
    notification_sent = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime(timezone=True))
    last_updated = db.Column(db.DateTime(),server_default=db.func.now(), onupdate=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    def __str__(self):
        return '%s' % (self.name)

class CirculatingOgnSupply(db.Model):
    __tablename__ = 'circulating_ogn_supply'
    id = db.Column(db.Integer, primary_key=True)
    supply_amount = db.Column(db.Float(), default=0)
    snapshot_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __str__(self):
        return '%s' % (self.name)

class CirculatingOgvSupply(db.Model):
    __tablename__ = 'circulating_ogv_supply'
    id = db.Column(db.Integer, primary_key=True)
    supply_amount = db.Column(db.Float(), default=0)
    snapshot_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __str__(self):
        return '%s' % (self.name)

class TokenInfo(db.Model):
    __tablename__ = 'token_info'
    id = db.Column(db.Integer, primary_key=True)
    total_supply = db.Column(db.String(255))
    holders = db.Column(db.Integer())
    transfers_count = db.Column(db.Integer())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __str__(self):
        return '%s' % (self.name)

@event.listens_for(Presale, 'after_insert')
@event.listens_for(Interest, 'after_insert')
def _subscribe_email_list(mapper, connection, target):
    from util.tasks import subscribe_email_list
    payload = {"email": target.email,
               "ip_addr": target.ip_addr}
    subscribe_email_list.delay(**payload)
