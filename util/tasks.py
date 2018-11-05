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
from database.db_models import EmailList, SocialPlatform
from fullcontact import FullContact
from random import randint
from sqlalchemy.exc import IntegrityError
from app import update_subscribed
from tools import db_utils
from sqlalchemy.orm.attributes import flag_modified

sites = []

sites.append({
    'name': 'Telegram',
    'url': 'http://t.me/originprotocol',
    'selector': 'div.tgme_page_extra',
    'json': False
})
sites.append({
    'name': 'Telegram (Korean)',
    'url': 'https://t.me/originprotocolkorea',
    'selector': 'div.tgme_page_extra',
    'json': False
})
sites.append({
    'name': 'Reddit',
    'url': 'https://old.reddit.com/r/originprotocol/',
    'selector': 'span.number',
    'json': False
})
sites.append({
    'name': 'Twitter',
    'url': 'https://twitter.com/originprotocol/',
    'selector': 'ul > li.ProfileNav-item.ProfileNav-item--following > a > span.ProfileNav-value',
    'json': False
})
sites.append({
    'name': 'Facebook',
    'url': 'https://www.facebook.com/originprotocol',
    'selector': '.clearfix ._ikh div._4bl9',
    'json': False
})
sites.append({
    'name': 'Youtube',
    'url': 'https://www.youtube.com/c/originprotocol',
    'selector': 'span.subscribed',
    'json': False
})
sites.append({
    'name': 'Naver',
    'url': 'https://section.blog.naver.com/connect/ViewMoreFollowers.nhn?blogId=originprotocol&widgetSeq=1',
    'selector': 'div.bg_main > div.container > div > div.content_box > div > div > p > strong',
    'json': False
})
sites.append({
    'name': 'KaKao plus friends',
    'url': 'https://pf.kakao.com/_qTxeYC',
    'selector': 'span.num_count',
    'json': False
})
sites.append({
    'name': 'Tencent/QQ video',
    'url': 'http://v.qq.com/vplus/c2564ca8e81c0debabe3c6c6aff3832c',
    'selector': '.user_count_play span.count_num',
    'json': False
})
sites.append({
    'name': 'Youku',
    'url': 'http://i.youku.com/originprotocol',
    'selector': 'div.user-state > ul > li.vnum em',
    'json': False
})
sites.append({
    'name': 'Weibo',
    'url': 'https://www.weibo.com/p/1005056598839228/home?from=page_100505&mod=TAB&is_hot=1#place',
    'selector': '#Pl_Core_T8CustomTriColumn__3 > div > div > div > table > tbody > tr > td:nth-of-type(2) > a > strong',
    'json': False
})
sites.append({
    'name': 'Medium',
    'url': 'https://medium.com/originprotocol?format=json',
    'selector': '',
    'json': True,
})

# This shows no followers
sites.append({
    'name': 'Steemit',
    'url': 'https://steemit.com/@originprotocol',
    'selector': 'div.UserProfile__stats > span:nth-of-type(1) > a',
    'json': False
})

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

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, update_subscribed_count.s(), name='update follower counts every 60')
    # sender.add_periodic_task(10.0, save_social_platforms.s(), name='add every 10')

@celery.task()
def send_email(body):
    logger.fatal("Sending email from Celery...")
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

@celery.task
def update_subscribed_count():
    with db_utils.request_context():
        platforms = SocialPlatform.query.all()
        for platform in platforms:
            try:
                updated_count = update_subscribed.update_subscribed(platform)
                if updated_count is None:
                    pass
                else:
                    print("I AM AN UPDATED PLATFORM", updated_count)
                    platform.subscribed_count = updated_count
                    flag_modified(platform, "subscribed_count")
                    db.session.merge(platform)
                    db.session.flush()
                    db.session.commit()

            except Exception as e:
                print("I AM ERRORING SILENTLY")
                logger.warning("Problem SocialPlatform", platform)
                db.session.rollback()
            finally:
                db.session.close()

@celery.task
def save_social_platforms():
    with db_utils.request_context():
        for site in sites:
            platform = db_models.SocialPlatform()
            platform.name = site['name']
            platform.url = site['url']
            platform.selector = site['selector']
            platform.json = site['json']

            try:
                db.session.add(platform)
                db.session.flush()
                db.session.commit()
                logger.info('Platform %s  added to social platform', platform)
            except IntegrityError as e:
                logger.warning("Platform %s has already been added to SocialPlatform table.", platform)
                db.session.rollback()
            finally:
                db.session.close()
