import json
import re

from config import constants
from config import universal
from database import db, db_common, db_models
from flask import jsonify, flash, redirect
from flask_babel import gettext, Babel, Locale
from logic.emails import email_types
from nameparser import HumanName
import pytest
import sendgrid
from tools import db_utils
from util import sendgrid_wrapper as sgw

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)

# we use our own database as the final source of truth for our mailing list
# but we sync email signups and unsubscribes to sendgrid for convenience

def add_sendgrid_contact(email, full_name=None, citizenship=None):
    pytest.skip("avoid making remote calls")
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    first_name = last_name = None
    if full_name:
        name = HumanName(full_name)
        first_name = name.first
        last_name = name.last

    data = [{
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "country_code": citizenship
    }]
    response = sg_api.client.contactdb.recipients.post(request_body=data)

def unsubscribe_sendgrid_contact(email):
    pytest.skip("avoid making remote calls")
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    unsubscribe_group = 51716 # Universal unsubscribe group

    data = {
        "recipient_emails": [email]
    }
    response = sg_api.client.asm.groups._(unsubscribe_group).suppressions.post(request_body=data)

def send_welcome(email, ip_addr):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return gettext('Please enter a valid email address')

    try:
        me = db_models.EmailList()
        me.email = email
        me.unsubscribed = False
        me.ip_addr = ip_addr
        db.session.add(me)
        db.session.commit()
    except:
        return gettext('You are already signed up!')

    email_types.send_email_type('welcome', DEFAULT_SENDER, email)

    return gettext('Thanks for signing up!')

def presale(full_name, email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note, ip_addr):

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
        me.ip_addr = ip_addr
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
                    ip_addr)

    email_types.send_email_type('presale', DEFAULT_SENDER, email)

    sgw.notify_founders(message, subject=full_name + " is interested in the presale")

    return gettext('Thanks! We\'ll be in touch soon.')

def unsubscribe(email):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return 'Please enter a valid email address'

    try:
        me = db_models.EmailList.query.filter_by(email=email).first()
        if me:
            # mark DB as unsubscribed in our DB
            me.unsubscribed = True
            db.session.commit()
    except Exception as e:
        print (e)
        return gettext('Ooops, something went wrong')

    return gettext('You have been unsubscribed')


def send_one_off(email_type):
    with db_utils.request_context():
        # the message log takes care of deduping emails that may appear in multiple tables
        for e in db_models.EmailList.query.filter_by(unsubscribed=False):
            print e.email
            email_types.send_email_type(email_type, DEFAULT_SENDER, e.email)


def partners_interest(name, company_name, email, website, note, ip_addr):

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
        me.ip_addr = ip_addr
        db.session.add(me)
        db.session.commit()
    except Exception as e:
        print (e)
        return gettext('Ooops! Something went wrong.')

    message = "Name: %s<br>Company Name: %s<br>Email: %s<br>Website: %s<br>Note: %s" % (name, company_name,
                                                                                        email, website, note)

    email_types.send_email_type('build_on_origin', DEFAULT_SENDER, email)

    sgw.notify_admins(message,
                      subject="{name} ({company_name}) is interested in building on Origin".format(name=name,
                                                                                                  company_name=company_name))

    return gettext('Thanks! We\'ll be in touch soon.')
