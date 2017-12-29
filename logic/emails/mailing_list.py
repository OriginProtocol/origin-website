import re

from flask import jsonify, flash, redirect

from config import universal
from database import db, db_common, db_models
from logic.emails import email_types
from util import sendgrid_wrapper as sgw

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)

def send_welcome(email):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return 'Please enter a valid email address'

    try:
        me = db_models.EmailList()
        me.email = email
        me.unsubscribed = False
        db.session.add(me)
        db.session.commit()
    except:
        return 'You are already signed up!'

    to_email = sgw.Email(email, email)
    email_types.send_email_type('welcome', DEFAULT_SENDER, to_email)

    return 'Thanks for signing up!'

def presale(email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return 'Please enter a valid email address'

    try:
        me = db_models.Presale()
        me.email = email
        me.accredited = accredited
        me.entity_type = entity_type
        me.desired_allocation = desired_allocation
        me.desired_allocation_currency = desired_allocation_currency
        me.citizenship = citizenship
        me.sending_addr = sending_addr
        me.note = note
        db.session.add(me)
        db.session.commit()
    except Exception as e:
         return 'Ooops! Something went wrong.'

    # to_email = sgw.Email(email, email)
    # email_types.send_email_type('welcome', DEFAULT_SENDER, to_email)

    return 'Thanks for signing up!'

def unsubscribe(email):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return 'Please enter a valid email address'

    try:
        me = db_models.EmailList.query \
            .filter(db_models.EmailList.email == email).first()
        me.unsubscribed = True
        db.session.commit()
    except Exception as e:
        return 'Ooops, something went wrong'

    return 'You have been unsubscribed'