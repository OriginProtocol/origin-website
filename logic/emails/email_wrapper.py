from config import constants
from util import sendgrid_wrapper as sgw

BCC_RECIPIENTS = [sgw.Email('founders@originprotocol.com', 'Founders')]

def send_email_msg(from_email, to_email, msg_subject, msg_category,
    msg_text, msg_html):

    try:
        categories = [msg_category]

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
                bccs=BCC_RECIPIENTS,
                categories=categories)

    except Exception as e:
        print to_email
        print str(e)
        sgw.notify_admins("Unable to send email message to " + to_email + " because \n\n" + str(e))

