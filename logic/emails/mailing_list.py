import json
import re

from config import constants
from config import universal
from database import db, db_common, db_models
from flask import jsonify, flash, redirect
from flask_babel import gettext, Babel, Locale
from logic.emails import email_types
from nameparser import HumanName
import sendgrid
from tools import db_utils
from util import sendgrid_wrapper as sgw
from util.misc import log

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)

# we use our own database as the final source of truth for our mailing list
# but we sync email signups and unsubscribes to sendgrid for convenience

def add_sendgrid_contact(email, full_name=None, country_code=None, dapp_user=None):
    try:
        # pytest.skip("avoid making remote calls")
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
            "country_code": country_code,
            "dapp_user": dapp_user
        }]
        response = sg_api.client.contactdb.recipients.post(request_body=data)
    except Exception as e:
        log('ERROR add_sendgrid_contact:', type(e), e)
        return False
    return True

def unsubscribe_sendgrid_contact(email):
    try:
        sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
        unsubscribe_group = 51716 # Universal unsubscribe group

        data = {
            "recipient_emails": [email]
        }
        response = sg_api.client.asm.groups._(unsubscribe_group).suppressions.post(request_body=data)
    except Exception as e:
        log('ERROR unsubscribe_sendgrid_contact:', type(e), e)
        return False
    return True

# Unsubscribe a list of emails.
def mass_unsubscribe_sendgrid_contact(emails):
    try:
        sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
        unsubscribe_group = 51716 # Universal unsubscribe group

        data = {
            "recipient_emails": emails
        }
        response = sg_api.client.asm.groups._(unsubscribe_group).suppressions.post(request_body=data)
    except Exception as e:
        log('ERROR mass_unsubscribe_sendgrid_contact:', type(e), e)
        return False
    return True

# Inserts or updates an entry in the email_list table.
# Returns True if a new entry was added, False if the entry already existed.
# Raises an exception in case of an error.
def add_contact(email, first_name, last_name, ip_addr, country_code):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        raise Exception('Invalid email')

    # Emails are stored normalized to lowercase in the DB.
    email = email.lower()
    try:
        # Attempt to load any existing entry matching the email.
        row = db_models.EmailList.query.filter_by(email=email).first()
        if row:
            # Update the existing entry.
            new_contact = False
            row.first_name = first_name
            row.last_name = last_name
            row.ip_addr = ip_addr
            row.country_code = country_code
        else:
            # Insert a new entry.
            new_contact = True
            row = db_models.EmailList()
            row.email = email
            row.first_name = first_name
            row.last_name = last_name
            row.unsubscribed = False
            row.ip_addr = ip_addr
            row.country_code = country_code
            db.session.add(row)
        db.session.commit()
    except Exception as e:
        log('ERROR add_contact:', type(e), e)
        raise e

    return new_contact

def send_welcome(email, source):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return

    if source is not None and source.lower() == 'ousd':
        email_types.send_email_type('welcome_ousd', DEFAULT_SENDER, email)
    else:
        email_types.send_email_type('welcome1', DEFAULT_SENDER, email)

def presale(full_name, email, desired_allocation, desired_allocation_currency, citizenship, sending_addr, ip_addr):

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return gettext('Please enter a valid email address')

    try:
        me = db_models.Presale()
        me.full_name = full_name
        me.email = email
        # me.accredited = (accredited=='1')
        # me.entity_type = entity_type
        me.desired_allocation = desired_allocation
        me.desired_allocation_currency = desired_allocation_currency
        me.citizenship = citizenship
        me.sending_addr = sending_addr
        # me.note = note
        me.ip_addr = ip_addr
        db.session.add(me)
        db.session.commit()
    except Exception as e:
        log('ERROR presale:', type(e), e)
        return gettext('Ooops! Something went wrong.')

    if sending_addr:
        sending_addr = "<a href='https://etherscan.io/address/"+sending_addr+"'>"+sending_addr+"</a>" if sending_addr.startswith('0x') else "<a href='https://blockchain.info/address/"+sending_addr+"'>"+sending_addr+"</a>"

    message = """Name: %s<br>
                 Email: %s<br>
                 Desired allocation: %s %s<br>
                 Citizenship: %s<br>
                 Address: %s<br>
                 IP: %s""" % (
                    full_name, email,
                    desired_allocation, desired_allocation_currency,
                    citizenship,
                    sending_addr,
                    ip_addr)

    email_types.send_email_type('presale', DEFAULT_SENDER, email)

    sgw.notify_founders(message, subject=full_name + " is interested in the presale")

    return gettext('Thanks! We\'ll be in touch soon.')

# Mark an email as unsubscribed in our DB.
# Raises an exception in case of an error.
def unsubscribe(email):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        raise Exception('Invalid email address')

    me = db_models.EmailList.query.filter_by(email=email.lower()).first()
    if not me:
        print("returning not me")
        return

    print("unsubscribing...")
    me.unsubscribed = True
    db.session.add(me)
    db.session.commit()

def send_one_off(email_type):
    with db_utils.request_context():
        # the message log takes care of deduping emails that may appear in multiple tables
        for e in db_models.EmailList.query.filter_by(unsubscribed=False):
            log(e.email)
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
        log('ERROR partners_interest:', type(e), e)
        return gettext('Ooops! Something went wrong.')

    message = "Name: %s<br>Company Name: %s<br>Email: %s<br>Website: %s<br>Note: %s" % (name, company_name,
                                                                                        email, website, note)

    email_types.send_email_type('build_on_origin', DEFAULT_SENDER, email)

    sgw.notify_admins(message,
                      subject="{name} ({company_name}) is interested in building on Origin".format(name=name,
                                                                                                  company_name=company_name))

    return gettext('Thanks! We\'ll be in touch soon.')

def list_cleanup():
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    response = sg_api.client.suppression.spam_reports.get()
    people = json.loads(response.body)
    print("Unsubscribing the following spam reporting email addresses:")
    for person in people:
            email = person['email'].lower()
            contact = db_models.EmailList.query.filter_by(email=email).first()
            # remove them from our marketing lists
            # unsubscribe_sendgrid_contact(email)
            print(person['email'])
            if contact:
                contact.spam_report = True
                contact.unsubscribed = True
                db.session.add(contact)
                db.session.commit()
    response = sg_api.client.suppression.invalid_emails.get()
    people = json.loads(response.body)
    print("Unsubscribing the following invalid email addresses:")
    for person in people:
            email = person['email'].lower()
            contact = db_models.EmailList.query.filter_by(email=email).first()
            # remove them from our marketing lists
            # unsubscribe_sendgrid_contact(email)
            print(person['email'])
            if contact:
                contact.invalid = True
                contact.unsubscribed = True
                db.session.add(contact)
                db.session.commit()
    response = sg_api.client.suppression.blocks.get()
    people = json.loads(response.body)
    print("Unsubscribing the following blocked email addresses:")
    for person in people:
            email = person['email'].lower()
            contact = db_models.EmailList.query.filter_by(email=email).first()
            # remove them from our marketing lists
            # unsubscribe_sendgrid_contact(email)
            print(person['email'])
            if contact:
                contact.blocked = True
                contact.unsubscribed = True
                db.session.add(contact)
                db.session.commit()
    response = sg_api.client.suppression.bounces.get()
    people = json.loads(response.body)
    print("Unsubscribing the following bounced email addresses:")
    for person in people:
        email = person['email'].lower()
        contact = db_models.EmailList.query.filter_by(email=email).first()
        # remove them from our marketing lists
        # unsubscribe_sendgrid_contact(email)
        print(person['email'])
        if contact:
            contact.bounced = True
            contact.unsubscribed = True
            db.session.add(contact)
            db.session.commit()
