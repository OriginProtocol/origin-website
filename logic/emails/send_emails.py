import re

from flask import jsonify

from config import universal
from database import db, db_common, db_models
from logic.emails import email_types
from util import sendgrid_wrapper as sgw

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)

def send_welcome(email):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return jsonify("Please enter a valid email address")

    try:
        me = db_models.EmailList()
        me.email = email
        me.unsubscribed = False
        db.session.add(me)
        db.session.commit()
    except:
        return jsonify('You are already signed up!')

    to_email = sgw.Email(email, email)
    email_types.send_email_type('welcome', DEFAULT_SENDER, to_email)

    return jsonify('Thanks for signing up!')