import os
import sendgrid
from app import app_config
from celery import Celery
from config import constants
from flask import Flask
from numpy.random import randint
from fullcontact import FullContact
import logic.emails.mailing_list
import logic.fullcontact.fullcontact

MIN_RETRY_TIME = 300
MAX_RETRY_TIME = 600

def make_celery(app):
    celery = Celery(app.import_name, backend=os.environ['REDIS_URL'],
                    broker=os.environ['REDIS_URL'],
                    )
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

flask_app.config.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_always_eager=os.environ.get('CELERY_DEBUG', False)
)


app_config.init_prod_app(flask_app)

celery = make_celery(flask_app)


@celery.task()
def send_email(body):
    flask_app.logger.fatal("Sending email from Celery...")
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    sg_api.client.mail.send.post(request_body=body)


@celery.task(rate_limit='300/m', max_retries=3)
def full_contact_request(email):
    fc = FullContact(constants.FULLCONTACT_KEY)
    r = fc.person(email=email)

    code = int(r.status_code)
    if code == 200:
        logic.fullcontact.fullcontact.fullcontact(email, r.json())
    elif code == 202:
        self.retry(countdown=randint(MIN_RETRY_TIME, MAX_RETRY_TIME))
    elif code == 404:
        logic.fullcontact.fullcontact.fullcontact(email, r.json())
    else:
        flask_app.logger.fatal("FullContact request %s with status code %s",
                               email, r.status_code)
        flask_app.logger.fatal(r.json())
