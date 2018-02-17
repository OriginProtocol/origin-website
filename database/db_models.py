
from decimal import *

from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from database import db, db_common


class EmailList(db.Model):
    __tablename__ = 'email_list'

    email = db.Column(db.String(255), primary_key=True, autoincrement=False)
    unsubscribed = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

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

    def __str__(self):
        return '%s' % (self.email)


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