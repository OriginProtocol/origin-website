import re

from flask import jsonify, flash, redirect

from config import universal
from database import db, db_common, db_models
from logic.emails import email_types
from util import sendgrid_wrapper as sgw
from tools import db_utils
from flask_babel import gettext, Babel, Locale

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)

def send_welcome(email):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return gettext('Please enter a valid email address')

    try:
        me = db_models.EmailList()
        me.email = email
        me.unsubscribed = False
        db.session.add(me)
        db.session.commit()
    except:
        return gettext('You are already signed up!')

    email_types.send_email_type('welcome', DEFAULT_SENDER, email)

    return gettext('Thanks for signing up!')

def presale(full_name, email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note, ip_address):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return gettext('Please enter a valid email address')

    try:
        me = db_models.Presale()
        me.full_name = full_name
        me.email = email
        me.accredited = (accredited=='1')
        me.entity_type = entity_type
        me.desired_allocation = desired_allocation
        me.desired_allocation_currency = desired_allocation_currency
        me.citizenship = citizenship
        me.sending_addr = sending_addr
        me.note = note
        db.session.add(me)
        db.session.commit()
    except Exception as e:
        print (e)
        return gettext('Ooops! Something went wrong.')

    if sending_addr:
        sending_addr = "<a href='https://etherscan.io/address/"+sending_addr+"'>"+sending_addr+"</a>" if sending_addr.startswith('0x') else "<a href='https://blockchain.info/address/"+sending_addr+"'>"+sending_addr+"</a>"

    message = """Name: %s<br>
                 Email: %s<br>
                 Accredited: %s<br>
                 Entity: %s<br>
                 Desired allocation: %s %s<br>
                 Citizenship: %s<br>
                 Address: %s<br>
                 Note: %s<br>
                 IP: %s""" % (
                    full_name, email,
                    ("Yes" if accredited == "1" else "No"),
                    entity_type,
                    desired_allocation, desired_allocation_currency,
                    citizenship,
                    sending_addr,
                    note,
                    ip_address)

    email_types.send_email_type('presale', DEFAULT_SENDER, email)

    sgw.notify_admins(message, subject=full_name + " is interested in the presale")

    return gettext('Thanks! We\'ll be in touch soon.')

def unsubscribe(email):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return 'Please enter a valid email address'

    try:
        me = db_models.EmailList.query \
            .filter(db_models.EmailList.email == email).first()
        me.unsubscribed = True
        db.session.commit()
    except Exception as e:
        print (e)
        return gettext('Ooops, something went wrong')

    return gettext('You have been unsubscribed')


def send_one_off(email_type):
    with db_utils.request_context():
        for e in db_models.Presale.query.all():
            print e.email
            email_types.send_email_type(email_type, DEFAULT_SENDER, e.email)

        for e in db_models.EmailList.query.all():
            print e.email
            email_types.send_email_type(email_type, DEFAULT_SENDER, e.email)


def build_interest(name, company_name, email, website, note):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return gettext('Please enter a valid email address')

    if website and not re.match(r"(^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$)", website):
        return gettext('Please enter a valid website address')

    try:
        me = db_models.Interest()
        me.name = name
        me.company_name = company_name
        me.email = email
        me.website = website
        me.note = note
        db.session.add(me)
        db.session.commit()
    except Exception as e:
        print (e)
        return gettext('Ooops! Something went wrong.')

    message = "Name: %s<br>Company Name: %s<br>Email: %s<br>Website: %s<br>Note: %s" % (name, company_name,
                                                                                        email, website, note)

    email_types.send_email_type('build_on_origin', DEFAULT_SENDER, email)

    sgw.notify_admins(message,
                      subject="{name}({company_name}) is interested in building on Origin".format(name=name,
                                                                                                  company_name=company_name))

    return gettext('Thanks! We\'ll be in touch soon.')
