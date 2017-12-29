from flask import render_template

from config import universal
from logic.emails import email_wrapper
from util import sendgrid_wrapper as sgw

EMAILS = {
    'welcome': {
        'subject': 'Welcome to Origin Protocol'
    }
}

def send_email_type(email_type, from_email, to_email):
    msg_subject = EMAILS.get(email_type).get('subject')
    msg_category = email_type

    msg_text = render_template('email/%s.txt' % email_type, universal=universal, to_email=to_email.email)
    msg_html = render_template('email/%s.html' % email_type, universal=universal, to_email=to_email.email)

    email_wrapper.send_email_msg(from_email, to_email, 
        msg_subject, msg_category, msg_text, msg_html)