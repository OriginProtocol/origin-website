from config import universal, constants
from database import db, db_models
from flask import render_template
from util import sendgrid_wrapper as sgw
from util import time_

DEFAULT_SENDER = sgw.Email(universal.CONTACT_EMAIL, universal.BUSINESS_NAME)
# BCC_RECIPIENTS = [sgw.Email('founders@originprotocol.com', 'Founders')]

# welcome1 is sent when they sign up
# welcome emails 2-5 are sent on a drip campaign

EMAILS = {
    'welcome1': {
        'subject': 'Thanks for joining Origin Protocol'
    },
    'welcome_ousd': {
        'subject': 'Thanks for joining Origin Protocol'
    },
    # 'welcome2': {
    #     'subject': 'Getting started with decentralized applications'
    # },
    # 'welcome3': {
    #     'subject': 'Welcome to the Origin marketplace'
    # },
    # 'welcome4': {
    #     'subject': 'Making your first purchase on Origin'
    # },
    # 'welcome5': {
    #     'subject': 'Start selling on Origin'
    # },
    'presale': {
        'subject': 'Thanks for your interest in Origin!'
    },
    'build_on_origin': {
        'subject': 'Thanks for your interest in partnering with Origin!'
    }
}

def send_email_type(email_type, from_email, to_email):

    # print email_type, from_email, to_email

    msg_subject = EMAILS.get(email_type).get('subject')

    msg_text = render_template('email/%s.txt' % email_type, universal=universal, to_email=to_email)
    msg_html = render_template('email/%s.html' % email_type, universal=universal, to_email=to_email)

    send_email_msg(from_email, to_email, 
        msg_subject, email_type, msg_text, msg_html)


def has_existing_message(to_email, msg_purpose):
    ML = db_models.MessageLog
    existing_msgs = ML.query.filter(ML.email == to_email)

    if msg_purpose:
        existing_msgs = existing_msgs.filter(ML.msg_purpose == msg_purpose)

    return existing_msgs.count()

def send_email_msg(from_email, to_email, msg_subject, msg_purpose,
    msg_text, msg_html):

    if not has_existing_message(to_email, msg_purpose):
        try:

            add_to_message_log(to_email, msg_purpose, msg_text, msg_subject, msg_html)

            try:    
                categories = [msg_purpose]

                if 'localhost' in constants.HOST or 'pagekite' in constants.HOST:
                    sgw.send_message(
                        sender=from_email,
                        recipients=[sgw.Email(constants.DEV_EMAIL, constants.DEV_EMAIL)],
                        subject='DEV: ' + msg_subject,
                        body_text=msg_text,
                        body_html=msg_html,
                        categories=categories)
                else:
                    sgw.send_message(
                        sender=from_email,
                        recipients=[sgw.Email(to_email, to_email)],
                        subject=msg_subject,
                        body_text=msg_text,
                        body_html=msg_html,
                        categories=categories)

            except Exception as e:
                sgw.notify_admins("Unable to send email message for " + to_email + " because \n\n" + str(e))

        except Exception as e:
            sgw.notify_admins("Unable to write to message log for " + to_email + " because \n\n" + str(e))

def add_to_message_log(email, msg_purpose, msg_text, msg_subject=None, msg_html=None):
    message_log = db_models.MessageLog(
    email=email,
    msg_purpose=msg_purpose,
    msg_subject=msg_subject,
    msg_text=msg_text,
    msg_html=msg_html)

    db.session.add(message_log)
    db.session.commit()


def send_welcome_drips():
    EL = db_models.EmailList
    db_users = EL.query.filter(EL.unsubscribed == False)

    # db_users_2_days = db_users.filter(EL.created_at <= time_.days_before_now(1)).filter(EL.created_at > time_.days_before_now(2))
    # for row in db_users_2_days:
    #     send_email_type('welcome2', DEFAULT_SENDER, row.email)

    # db_users_3_days = db_users.filter(EL.created_at <= time_.days_before_now(2)).filter(EL.created_at > time_.days_before_now(3))
    # for row in db_users_3_days:
    #     send_email_type('welcome3', DEFAULT_SENDER, row.email)

    # TODO: let's try the initial 3 emails out first before adding these to the campaign
    # db_users_4_days = db_users.filter(EL.created_at <= time_.days_before_now(3)).filter(EL.created_at > time_.days_before_now(4))
    # for row in db_users_4_days:
    #     send_email_type('welcome4', DEFAULT_SENDER, row.email)

    # db_users_5_days = db_users.filter(EL.created_at <= time_.days_before_now(4)).filter(EL.created_at > time_.days_before_now(5))
    # for row in db_users_5_days:
    #     send_email_type('welcome5', DEFAULT_SENDER, row.email)




