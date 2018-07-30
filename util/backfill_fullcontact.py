# -*- coding: utf-8 -*-
"""
This file "backfills" fullcontact information.
Ordinarily fullcontact info is retrieved at the time user info is entered,
but we have a lot of preexisting data. This one-time script will catch us up.

Example to process next 10 emails:
    python util/backfill_fullcontact.py -l 10

Setup and useful tools:

Start Redis in own tab:
    redis-server

Start Celery in own tab:
    celery -A util.tasks worker

To purge all pending tasks:
    # Stop celery worker first
    celery -A util.tasks purge

If testing locally, origin-box may be using the default redis port.
Fix by using different port:
    redis-server --port 6380
    export REDIS_URL="redis://localhost:6380/0"

Celery Flower is useful GUI for monitoring:
    pip install flower
    flower -A util.tasks --port=5555
    open 127.0.0.1:5555

SQL to count emails left to process:
    SELECT COUNT(DISTINCT presale.email)
    FROM presale
        LEFT JOIN fullcontact ON presale.email = fullcontact.email
    WHERE fullcontact.id IS NULL

"""

import os
import sys
import argparse
from app import app_config
from config import constants

from database import db
from flask import Flask

from logic.emails import email_types

flask_app = Flask(__name__)

flask_app.config.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_always_eager=os.environ.get('CELERY_DEBUG', False)
)

app_config.init_prod_app(flask_app)

import tasks

def backfill_fullcontact(limit=100000):
    with flask_app.app_context():

        # Find users for whom we have no fullcontact info
        unfilled = """
            SELECT DISTINCT presale.email
            FROM presale
                LEFT JOIN fullcontact ON presale.email = fullcontact.email
            WHERE fullcontact.id IS NULL
            LIMIT %d
        """ % (limit)
        result = db.engine.execute(unfilled)

        for row in result:
            print ("Creating task for email: %s" % row[0])
            tasks.full_contact_request.delay(row[0])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Backfill missing fullcontact data on emails from presale table.')

    parser.add_argument('-l', '--limit', default=100000, type=int,
                        help='number of rows it will attempt (default: find the max)')

    args = parser.parse_args()

    if ('REDIS_URL' not in os.environ):
        sys.exit("REDIS_URL is not set.")
    if ('FULLCONTACT_KEY' not in os.environ):
        sys.exit("FULLCONTACT_KEY is not set.")
    if ('DATABASE_URL' not in os.environ):
        sys.exit("DATABASE_URL is not set.")

    backfill_fullcontact(args.limit)
