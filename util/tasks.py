import os
import sendgrid
from celery import Celery
from config import constants
from flask import Flask
from database import db

from database.db_models import EmailList


def make_celery(app):
    celery = Celery(app.import_name, backend=os.environ['REDIS_URL'],
                    broker=os.environ['REDIS_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

flask_app = Flask(__name__)


# TODO: (Gzing) - A lot of celery configuration level stuff can be moved to app_config
# instead of being defined at multiple places.

flask_app.config.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_always_eager=(os.environ.get('CELERY_DEBUG') == 'True'),
    SQLALCHEMY_DATABASE_URI=constants.SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=False,
)

db.init_app(flask_app)
celery = make_celery(flask_app)


@celery.task()
def send_email(body):
    flask_app.logger.fatal("Sending email from Celery...")
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    sg_api.client.mail.send.post(request_body=body)


@celery.task()
def subscribe_email_list(**kwargs):
    email = kwargs.get('email')
    ip_addr = kwargs.get('ip_addr')
    if not email and ip_addr:
        return
    is_subscriber = EmailList.query.filter_by(email=email).first()
    if not is_subscriber:
        db.session.add(EmailList(email=email,
                                 ip_addr=ip_addr,
                                 unsubscribed=False))
        db.session.commit()
