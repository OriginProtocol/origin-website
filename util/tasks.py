# -*- coding: utf-8 -*-
"""
This file handles asyncronous tasks.
Tasks are performed using Celery (http://www.celeryproject.org/)
Task functions are at bottom of file, and decorated with `@celery.task()`
"""

import os
import sendgrid
from celery import Celery
from celery.utils.log import get_task_logger
from config import constants
from flask import Flask
from database import db, db_models
from database.db_models import EmailList
from fullcontact import FullContact
from random import randint
from sqlalchemy.exc import IntegrityError

# Get logger for tasks
logger = get_task_logger(__name__)

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
    logger.fatal("Sending email from Celery...")
    sg_api = sendgrid.SendGridAPIClient(api_key=constants.SENDGRID_API_KEY)
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

@celery.task(
    rate_limit=os.environ.get('FULLCONTACT_RATE_LIMIT', '30/m'),
    max_retries=3,
    name='tasks.full_contact_request')
def full_contact_request(email):
    """ Request fullcontact info based on email """

    if (constants.FULLCONTACT_KEY is None):
        logger.fatal("constants.FULLCONTACT_KEY is not set.")
        return

    logger.info('Looking up %s', email)

    fc = FullContact(constants.FULLCONTACT_KEY)
    r = fc.person(email=email)

    MIN_RETRY_SECS = 10
    MAX_RETRY_SECS = 600

    code = int(r.status_code)
    if (code == 200) or (code == 404):
        # Success or not found
        # (We log "not found" results in db too, so that we know
        # we tried and can move on to next email.)
        contact_json = r.json()
        fc_row = db_models.FullContact()
        fc_row.email = email
        fc_row.fullcontact_response = contact_json

        if 'socialProfiles' in contact_json:
            profiles = contact_json['socialProfiles']
            for profile in profiles:
                if 'typeId' in profile and 'username' in profile:
                    network = profile['typeId']
                    username = profile['username']
                    if network == 'angellist':
                        fc_row.angellist_handle = username
                    if network == 'github':
                        fc_row.github_handle = username
                    if network == 'twitter':
                        fc_row.twitter_handle = username
        try:
            db.session.add(fc_row)
            db.session.commit()
            logger.info('Email %s  recorded to fullcontact', email)
        except IntegrityError as e:
            logger.warning("Email %s has already been entered in FullContact table.", email)
    elif code == 403:
        # Key fail
        logger.fatal("constants.FULLCONTACT_KEY is not set or is invalid.")
    elif code == 202:
        # We're requesting too quickly, randomly back off
        delay = randint(MIN_RETRY_SECS, MAX_RETRY_SECS)
        logger.warning("Throttled by FullContact. Retrying after random delay of %d" % delay)
        full_contact_request.retry(countdown=delay)
    else:
        logger.fatal("FullContact request %s with status code %s",
                               email, r.status_code)
        logger.fatal(r.json())
