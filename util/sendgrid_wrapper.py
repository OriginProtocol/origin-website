import sendgrid.helpers.mail as sgh
from config import constants
import os

# Use Redis to send mail only if env var present.
if os.environ.get('REDIS_URL') is not None:
    from .tasks import send_email
else:
    def send_email(body):
        print("Email disabled.")
        return

class Email(object):
    def __init__(self, email, name):
        self.email = email
        self.name = name

class Attachment(object):
    def __init__(self, content, type, filename, disposition, content_id):
        self.content = content
        self.type = type
        self.filename = filename
        self.disposition = disposition
        self.content_id = content_id

def notify_admins(message, subject=None):
    return notify_(message, subject, Email('info@originprotocol.com', 'Origin Team'))

def notify_founders(message, subject=None):
    return notify_(message, subject, Email('founders@originprotocol.com', 'Origin Founders'))

def notify_(message, subject=None, to_notify=None):
    subject = subject.encode('ascii', 'ignore') if subject else None
    if 'localhost' in constants.HOST or 'pagekite' in constants.HOST:
        recipients=[Email(constants.DEV_EMAIL, constants.DEV_EMAIL)]
        subject = 'DEV: ' + str(subject) if subject else str(message)
    else:
        recipients = [to_notify]
        subject = str(subject) if subject else str(message)
    send_message(
        sender=Email('bot@originprotocol.com', 'Emily the bot'),
        recipients=recipients,
        subject=subject,
        body_text=message,
        body_html=message,
        categories=['admin'])


def send_message(sender, recipients, subject, body_text, body_html,
    attachments=None, ccs=None, bccs=None, categories=None, send=True):
    mail = sgh.Mail()
    mail.from_email = sgh.Email(sender.email, sender.name)
    mail.subject = subject

    for recipient in recipients:
        personalization = sgh.Personalization()
        personalization.add_to(sgh.Email(recipient.email, recipient.name))

        if ccs:
            for cc in ccs:
                personalization.add_cc(sgh.Email(cc.email))
        if bccs:
            for bcc in bccs:
                personalization.add_bcc(sgh.Email(bcc.email))
        mail.add_personalization(personalization)

    mail.add_content(sgh.Content("text/plain", body_text))
    mail.add_content(sgh.Content("text/html", body_html))

    if attachments:
        for attach in attachments:
            attachment = sgh.Attachment()
            attachment.set_content(attach.content)
            attachment.set_type(attach.type)
            attachment.set_filename(attach.filename)
            attachment.set_disposition(attach.disposition)
            attachment.set_content_id(attach.content_id)
            mail.add_attachment(attachment)
    if categories:
        for category in categories:
            mail.add_category(sgh.Category(category))
    if send:
        if os.environ.get('REDIS_URL') is not None:
            send_email.delay(body=mail.get())
        else:
            import sendgrid
            sg_api = sendgrid.SendGridAPIClient(api_key=constants.SENDGRID_API_KEY)
            return sg_api.client.mail.send.post(request_body=mail.get()) 
